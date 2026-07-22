const db = require('../../db');

class WorkflowEngine {
  /**
   * Matches rules against transaction parameter bounds and initiates approval lifecycle.
   */
  async initiateWorkflow(module, entityId, amount, departmentId = null, budgetHead = null) {
    try {
      // 1. Fetch active rules for this module
      let ruleQuery = `
        SELECT * FROM workflow_rules 
        WHERE module = $1 
        AND min_amount <= $2 
        AND max_amount >= $2
      `;
      let params = [module, amount];

      if (departmentId) {
        ruleQuery += ' AND (department_id = $3 OR department_id IS NULL)';
        params.push(departmentId);
      } else {
        ruleQuery += ' AND department_id IS NULL';
      }

      const ruleRes = await db.query(ruleQuery, params);
      let matchedRules = ruleRes.rows;

      // Filter by conditional criteria (e.g. capex/opex)
      if (budgetHead) {
        matchedRules = matchedRules.filter(rule => {
          if (rule.conditional_type === 'capex_only') return budgetHead.toLowerCase() === 'capex';
          if (rule.conditional_type === 'opex_only') return budgetHead.toLowerCase() === 'opex';
          return true;
        });
      }

      if (matchedRules.length === 0) {
        console.log(`No workflow rules defined for module '${module}' with amount ${amount}.`);
        return null;
      }

      // Sort rules by sequence step to establish chain
      matchedRules.sort((a, b) => a.step_sequence - b.step_sequence);

      // 2. Create Instance
      const instanceRes = await db.query(
        `INSERT INTO workflow_instances (module, entity_id, status)
         VALUES ($1, $2, 'pending')
         ON CONFLICT (module, entity_id) DO UPDATE SET status = 'pending', updated_at = NOW()
         RETURNING id`,
        [module, entityId]
      );
      const instanceId = instanceRes.rows[0].id;

      // Clean old steps if re-submitted
      await db.query('DELETE FROM workflow_steps WHERE instance_id = $1', [instanceId]);

      // 3. Populate steps and calculate SLA due times
      for (const rule of matchedRules) {
        const slaHours = rule.sla_hours || 24;
        const dueAt = new Date();
        dueAt.setHours(dueAt.getHours() + slaHours);

        // Assign default user for this role/department if exists in system
        let assignedUserId = null;
        const userQuery = `
          SELECT u.id 
          FROM users u
          JOIN user_profiles p ON u.id = p.user_id
          WHERE p.role_name = $1
          ${departmentId ? 'AND (p.department_id = $2 OR p.department_id IS NULL)' : ''}
          LIMIT 1
        `;
        const userParams = [rule.required_role_name];
        if (departmentId) userParams.push(departmentId);

        const assignedUserRes = await db.query(userQuery, userParams);
        if (assignedUserRes.rows.length > 0) {
          assignedUserId = assignedUserRes.rows[0].id;
        }

        await db.query(
          `INSERT INTO workflow_steps (instance_id, step_sequence, assigned_role_name, assigned_user_id, status, sla_hours, due_at)
           VALUES ($1, $2, $3, $4, $5, $6, $7)`,
          [
            instanceId,
            rule.step_sequence,
            rule.required_role_name,
            assignedUserId,
            rule.step_sequence === 1 ? 'pending' : 'queued', // first step is active, rest queued
            slaHours,
            dueAt
          ]
        );
      }

      console.log(`Workflow instance ${instanceId} initiated successfully with ${matchedRules.length} steps.`);
      return instanceId;
    } catch (error) {
      console.error('Error initiating workflow:', error);
      throw error;
    }
  }
}

module.exports = new WorkflowEngine();
