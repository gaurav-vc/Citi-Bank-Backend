const db = require('../../db');

class WorkflowController {
  async getPendingApprovals(req, res, next) {
    try {
      const { role, id: userId } = req.user;

      // Query steps where status is pending and matches user's active RBAC role or user ID
      const result = await db.query(
        `SELECT s.id as step_id, s.step_sequence, s.due_at, i.module, i.entity_id, i.created_at as initiated_at
         FROM workflow_steps s
         JOIN workflow_instances i ON s.instance_id = i.id
         WHERE s.status = 'pending' 
         AND (s.assigned_role_name = $1 OR s.assigned_user_id = $2 OR s.escalated_to_role = $1)`,
        [role, userId]
      );

      return res.json(result.rows);
    } catch (err) {
      next(err);
    }
  }

  async actionStep(req, res, next) {
    const client = await db.connect();
    try {
      const { step_id, action, comments } = req.body; // action: 'approve' or 'reject'
      const userId = req.user.id;

      if (!step_id || !action) {
        return res.status(400).json({ error: 'step_id and action are required' });
      }

      await client.query('BEGIN');

      // 1. Fetch current step
      const stepRes = await client.query(
        'SELECT * FROM workflow_steps WHERE id = $1 AND status = $2',
        [step_id, 'pending']
      );
      if (stepRes.rows.length === 0) {
        await client.query('ROLLBACK');
        return res.status(404).json({ error: 'Pending workflow step not found' });
      }
      const currentStep = stepRes.rows[0];
      const instanceId = currentStep.instance_id;

      if (action === 'reject') {
        // Mark current step as rejected
        await client.query(
          `UPDATE workflow_steps 
           SET status = 'rejected', actioned_at = NOW(), actioned_by = $1, comments = $2
           WHERE id = $3`,
          [userId, comments || null, step_id]
        );
        // Mark instance as rejected
        await client.query(
          "UPDATE workflow_instances SET status = 'rejected', updated_at = NOW() WHERE id = $1",
          [instanceId]
        );
        
        // Custom Hook: Update the target transaction state e.g. indent status
        const instRes = await client.query('SELECT * FROM workflow_instances WHERE id = $1', [instanceId]);
        const instance = instRes.rows[0];
        if (instance.module === 'indents') {
          await client.query("UPDATE indents SET status = 'rejected' WHERE id = $1", [instance.entity_id]);
        } else if (instance.module === 'payments') {
          await client.query("UPDATE payment_proposals SET status = 'rejected' WHERE id = $1", [instance.entity_id]);
        }

        await client.query('COMMIT');
        return res.json({ message: 'Workflow step rejected successfully.' });
      }

      // Action is Approve
      await client.query(
        `UPDATE workflow_steps 
         SET status = 'approved', actioned_at = NOW(), actioned_by = $1, comments = $2
         WHERE id = $3`,
        [userId, comments || null, step_id]
      );

      // Check if there is a next step in queue
      const nextStepRes = await client.query(
        `SELECT * FROM workflow_steps 
         WHERE instance_id = $1 AND step_sequence = $2`,
        [instanceId, currentStep.step_sequence + 1]
      );

      if (nextStepRes.rows.length > 0) {
        const nextStep = nextStepRes.rows[0];
        // Calculate new due date starting from now
        const newDue = new Date();
        newDue.setHours(newDue.getHours() + nextStep.sla_hours);

        await client.query(
          `UPDATE workflow_steps 
           SET status = 'pending', due_at = $1 
           WHERE id = $2`,
          [newDue, nextStep.id]
        );
      } else {
        // No next step -> Entire Workflow Approved!
        await client.query(
          "UPDATE workflow_instances SET status = 'approved', updated_at = NOW() WHERE id = $1",
          [instanceId]
        );

        // Custom Hook: Update target transaction state to Approved
        const instRes = await client.query('SELECT * FROM workflow_instances WHERE id = $1', [instanceId]);
        const instance = instRes.rows[0];
        if (instance.module === 'indents') {
          await client.query("UPDATE indents SET status = 'hod_approved' WHERE id = $1", [instance.entity_id]);
        } else if (instance.module === 'payments') {
          await client.query("UPDATE payment_proposals SET status = 'approved' WHERE id = $1", [instance.entity_id]);
        }
      }

      await client.query('COMMIT');
      return res.json({ message: 'Workflow step approved successfully.' });
    } catch (err) {
      await client.query('ROLLBACK');
      next(err);
    } finally {
      client.release();
    }
  }

  // Automatic SLA Escalation logic
  async escalateOverdueSteps(req, res, next) {
    try {
      // Find all pending steps past their SLA due dates
      const result = await db.query(
        `SELECT s.id, s.assigned_role_name, i.module, i.entity_id 
         FROM workflow_steps s
         JOIN workflow_instances i ON s.instance_id = i.id
         WHERE s.status = 'pending' AND s.due_at < NOW()`
      );

      const escalationMap = {
        'site_engineer': 'facility_manager',
        'store_keeper': 'procurement_executive',
        'procurement_executive': 'procurement_manager',
        'procurement_manager': 'cxo',
        'finance_executive': 'finance_manager',
        'finance_manager': 'cxo'
      };

      let escalatedCount = 0;
      for (const step of result.rows) {
        const nextRole = escalationMap[step.assigned_role_name];
        if (nextRole) {
          // Escalate to senior role
          await db.query(
            `UPDATE workflow_steps 
             SET escalated_to_role = $1, status = 'pending', comments = COALESCE(comments, '') || ' [Auto-Escalated due to SLA Breach]'
             WHERE id = $2`,
            [nextRole, step.id]
          );
          escalatedCount++;
          console.log(`Step ${step.id} for ${step.module} ${step.entity_id} escalated to ${nextRole}`);
        }
      }

      return res.json({ message: `SLA escalation run completed. Escalated ${escalatedCount} overdue steps.` });
    } catch (err) {
      next(err);
    }
  }
}

module.exports = new WorkflowController();
