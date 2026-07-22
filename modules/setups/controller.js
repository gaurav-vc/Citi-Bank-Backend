const db = require('../../db');

class SetupsController {
  async getRoles(req, res, next) {
    try {
      const result = await db.query('SELECT * FROM roles ORDER BY role_name');
      return res.json(result.rows);
    } catch (err) {
      next(err);
    }
  }

  async getDepartments(req, res, next) {
    try {
      const result = await db.query(`
        SELECT d.*, s.name as site_name 
        FROM departments d
        LEFT JOIN sites s ON d.site_id = s.id
        ORDER BY d.name
      `);
      return res.json(result.rows);
    } catch (err) {
      next(err);
    }
  }

  async getOrganizations(req, res, next) {
    try {
      const result = await db.query('SELECT * FROM organizations ORDER BY name');
      return res.json(result.rows);
    } catch (err) {
      next(err);
    }
  }

  async createOrganization(req, res, next) {
    try {
      const { name, code } = req.body;
      if (!name || !code) {
        return res.status(400).json({ error: 'Organization name and code are required' });
      }
      const result = await db.query(
        'INSERT INTO organizations (name, code) VALUES ($1, $2) RETURNING *',
        [name, code]
      );
      return res.status(201).json(result.rows[0]);
    } catch (err) {
      next(err);
    }
  }

  async getSites(req, res, next) {
    try {
      const result = await db.query(`
        SELECT s.*, o.name as organization_name 
        FROM sites s
        JOIN organizations o ON s.organization_id = o.id
        ORDER BY s.name
      `);
      return res.json(result.rows);
    } catch (err) {
      next(err);
    }
  }

  async createSite(req, res, next) {
    try {
      const { organization_id, name, code } = req.body;
      if (!organization_id || !name || !code) {
        return res.status(400).json({ error: 'Organization ID, site name, and site code are required' });
      }
      const result = await db.query(
        'INSERT INTO sites (organization_id, name, code) VALUES ($1, $2, $3) RETURNING *',
        [organization_id, name, code]
      );
      return res.status(201).json(result.rows[0]);
    } catch (err) {
      next(err);
    }
  }

  async createDepartment(req, res, next) {
    try {
      const { name, site_id, description } = req.body;
      if (!name || !site_id) {
        return res.status(400).json({ error: 'Department name and Site ID are required' });
      }
      const result = await db.query(
        'INSERT INTO departments (name, site_id, description) VALUES ($1, $2, $3) RETURNING *',
        [name, site_id, description || null]
      );
      return res.status(201).json(result.rows[0]);
    } catch (err) {
      next(err);
    }
  }

  async getUsersHierarchy(req, res, next) {
    try {
      const result = await db.query(`
        SELECT u.id as user_id, u.name as user_name, u.email, u.role as static_role,
               p.id as profile_id, p.phone_number, p.role_name as rbac_role,
               o.id as org_id, o.name as organization_name,
               s.id as site_id, s.name as site_name,
               d.id as dept_id, d.name as department_name
        FROM users u
        LEFT JOIN user_profiles p ON u.id = p.user_id
        LEFT JOIN organizations o ON p.organization_id = o.id
        LEFT JOIN sites s ON p.site_id = s.id
        LEFT JOIN departments d ON p.department_id = d.id
        ORDER BY u.name
      `);
      return res.json(result.rows);
    } catch (err) {
      next(err);
    }
  }

  async assignUserHierarchy(req, res, next) {
    try {
      const { user_id, organization_id, site_id, department_id, role_name } = req.body;

      if (!user_id) {
        return res.status(400).json({ error: 'User ID is required' });
      }

      // Update basic user static role if mapped
      if (role_name) {
        const dbRoles = [
          'site_engineer', 'store_keeper', 'procurement_executive', 'procurement_manager',
          'finance_executive', 'finance_manager', 'facility_manager', 'project_head', 'vendor', 'cxo'
        ];
        // Parse friendly name into static constraint fallback if possible
        let staticRole = 'site_engineer';
        if (dbRoles.includes(role_name.toLowerCase().replace(' ', '_'))) {
          staticRole = role_name.toLowerCase().replace(' ', '_');
        }
        await db.query('UPDATE users SET role = $1 WHERE id = $2', [staticRole, user_id]);
      }

      // Upsert User Profile references
      const result = await db.query(
        `INSERT INTO user_profiles (user_id, organization_id, site_id, department_id, role_name)
         VALUES ($1, $2, $3, $4, $5)
         ON CONFLICT (user_id) DO UPDATE SET
           organization_id = EXCLUDED.organization_id,
           site_id = EXCLUDED.site_id,
           department_id = EXCLUDED.department_id,
           role_name = EXCLUDED.role_name
         RETURNING *`,
        [
          user_id,
          organization_id || null,
          site_id || null,
          department_id || null,
          role_name || null
        ]
      );

      return res.json({
        message: 'User hierarchy and role assignment completed successfully',
        profile: result.rows[0]
      });
    } catch (err) {
      next(err);
    }
  }

  async getModulesAndFeatures(req, res, next) {
    try {
      const modulesRes = await db.query('SELECT * FROM app_modules ORDER BY module_order');
      const featuresRes = await db.query('SELECT * FROM app_features');
      
      const modules = modulesRes.rows.map(mod => {
        return {
          id: mod.id,
          title: mod.name,
          order: mod.module_order,
          items: featuresRes.rows.filter(f => f.module_id === mod.id).map(f => ({
            key: f.feature_key,
            label: f.label
          }))
        };
      });
      return res.json(modules);
    } catch (err) {
      next(err);
    }
  }

  async getMappings(req, res, next) {
    try {
      const result = await db.query(`
        SELECT r.id, ro.role_name, d.name as department_name, r.permissions
        FROM role_access_mappings r
        JOIN roles ro ON r.role_id = ro.id
        LEFT JOIN departments d ON r.department_id = d.id
      `);
      return res.json(result.rows);
    } catch (err) {
      next(err);
    }
  }

  async syncMapping(req, res, next) {
    try {
      const { role_name, department_name, permissions } = req.body;

      if (!role_name || !permissions) {
        return res.status(400).json({ error: 'role_name and permissions are required' });
      }

      // 1. Get Role ID
      const roleRes = await db.query('SELECT id FROM roles WHERE role_name = $1', [role_name]);
      if (roleRes.rows.length === 0) {
        return res.status(404).json({ error: 'Role not found' });
      }
      const roleId = roleRes.rows[0].id;

      // 2. Get Department ID if provided
      let deptId = null;
      if (department_name) {
        const deptRes = await db.query('SELECT id FROM departments WHERE name = $1', [department_name]);
        if (deptRes.rows.length === 0) {
          return res.status(404).json({ error: 'Department not found' });
        }
        deptId = deptRes.rows[0].id;
      }

      // 3. Upsert Access Mapping
      let result;
      if (deptId) {
        result = await db.query(`
          INSERT INTO role_access_mappings (role_id, department_id, permissions)
          VALUES ($1, $2, $3)
          ON CONFLICT (role_id, department_id) DO UPDATE SET permissions = EXCLUDED.permissions
          RETURNING *;
        `, [roleId, deptId, JSON.stringify(permissions)]);
      } else {
        const existing = await db.query(
          'SELECT id FROM role_access_mappings WHERE role_id = $1 AND department_id IS NULL',
          [roleId]
        );
        if (existing.rows.length > 0) {
          result = await db.query(
            'UPDATE role_access_mappings SET permissions = $1 WHERE id = $2 RETURNING *',
            [JSON.stringify(permissions), existing.rows[0].id]
          );
        } else {
          result = await db.query(
            'INSERT INTO role_access_mappings (role_id, department_id, permissions) VALUES ($1, NULL, $2) RETURNING *',
            [roleId, JSON.stringify(permissions)]
          );
        }
      }

      return res.status(200).json({
        message: 'Role Access Mapping synced successfully',
        mapping: result.rows[0]
      });
    } catch (err) {
      next(err);
    }
  }

  async seedDefaults(req, res, next) {
    try {
      const moduleCheck = await db.query('SELECT id FROM app_modules LIMIT 1');
      if (moduleCheck.rows.length > 0) {
        return res.json({ message: 'App Modules already seeded' });
      }

      // Seed modules and features like Django setups seed_defaults
      const defaults = [
        { name: 'Core Features', order: 0, features: [
          { key: 'core:dashboard', label: 'Dashboard' },
          { key: 'core:users', label: 'User Management' }
        ]},
        { name: 'Procurement', order: 1, features: [
          { key: 'procurement:vendors', label: 'Vendor Master' },
          { key: 'procurement:items', label: 'Item/Service Master' },
          { key: 'procurement:contracts', label: 'Rate Contract/AMC' },
          { key: 'procurement:budgets', label: 'Budget Master' },
          { key: 'procurement:indents', label: 'Requisitions/Indents' },
          { key: 'procurement:rfqs', label: 'Tendering/RFQs' },
          { key: 'procurement:orders', label: 'Purchase Orders' }
        ]},
        { name: 'Inventory', order: 2, features: [
          { key: 'procurement:inventory', label: 'Inventory Management' },
          { key: 'procurement:grn', label: 'GRN Entry' }
        ]},
        { name: 'Quality Inspection', order: 3, features: [
          { key: 'procurement:qc', label: 'QC & Service Entry' }
        ]},
        { name: 'Finance & Billing', order: 4, features: [
          { key: 'procurement:billing', label: 'Billing Invoices' },
          { key: 'procurement:payments', label: 'Payment Processing' },
          { key: 'procurement:expenses', label: 'Expense Management' }
        ]},
        { name: 'Reports & Analytics', order: 5, features: [
          { key: 'procurement:reports', label: 'Analytics Reports' },
          { key: 'procurement:ai', label: 'AI Spend Insights' }
        ]}
      ];

      for (const mod of defaults) {
        const modRes = await db.query(
          'INSERT INTO app_modules (name, module_order) VALUES ($1, $2) RETURNING id',
          [mod.name, mod.order]
        );
        const modId = modRes.rows[0].id;
        
        for (const feat of mod.features) {
          await db.query(
            'INSERT INTO app_features (module_id, feature_key, label) VALUES ($1, $2, $3)',
            [modId, feat.key, feat.label]
          );
        }
      }

      return res.json({ message: 'App Modules and features seeded successfully!' });
    } catch (err) {
      next(err);
    }
  }
}

module.exports = new SetupsController();
