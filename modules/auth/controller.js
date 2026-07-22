const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const db = require('../../db');

class AuthController {
  async register(req, res, next) {
    try {
      const { email, password, name, role, department, tower } = req.body;

      if (!email || !password || !name || !role) {
        return res.status(400).json({ error: 'Missing required fields' });
      }

      // Check user
      const existingUser = await db.query('SELECT id FROM users WHERE email = $1', [email]);
      if (existingUser.rows.length > 0) {
        return res.status(409).json({ error: 'Email already in use' });
      }

      const hashedPassword = await bcrypt.hash(password, 12);

      // 1. Create User
      const userRes = await db.query(
        `INSERT INTO users (email, password, name, role, department, tower)
         VALUES ($1, $2, $3, $4, $5, $6)
         RETURNING id, email, name, role, department, tower, created_at`,
        [email, hashedPassword, name, role, department || null, tower || null]
      );
      const user = userRes.rows[0];

      // 2. Create UserProfile
      let deptId = null;
      if (department) {
        const deptRes = await db.query('SELECT id FROM departments WHERE name = $1', [department]);
        if (deptRes.rows.length > 0) deptId = deptRes.rows[0].id;
      }

      await db.query(
        `INSERT INTO user_profiles (user_id, role_name, department_id)
         VALUES ($1, $2, $3)`,
        [user.id, role, deptId]
      );

      const token = jwt.sign(
        {
          id: user.id,
          email: user.email,
          name: user.name,
          role: user.role,
          department: user.department,
          tower: user.tower,
          permissions: {}
        },
        process.env.JWT_SECRET,
        { expiresIn: '7d' }
      );

      return res.status(201).json({ token, user });
    } catch (err) {
      next(err);
    }
  }

  async login(req, res, next) {
    try {
      const { email, password } = req.body;

      if (!email || !password) {
        return res.status(400).json({ error: 'Email and password are required' });
      }

      const result = await db.query('SELECT * FROM users WHERE email = $1', [email]);
      if (result.rows.length === 0) {
        return res.status(401).json({ error: 'Invalid email or password' });
      }

      const user = result.rows[0];
      const isMatch = await bcrypt.compare(password, user.password);
      if (!isMatch) {
        return res.status(401).json({ error: 'Invalid email or password' });
      }

      // 1. Fetch Dynamic RBAC Permissions mapping
      let permissions = {};
      try {
        const permResult = await db.query(
          `SELECT r.permissions 
           FROM role_access_mappings r
           JOIN roles ro ON r.role_id = ro.id
           LEFT JOIN departments d ON r.department_id = d.id
           WHERE ro.role_name = $1 
           AND (d.name = $2 OR r.department_id IS NULL)`,
          [user.role, user.department]
        );
        if (permResult.rows.length > 0) {
          permissions = permResult.rows[0].permissions;
        }
      } catch (err) {
        console.error('Error fetching dynamic permissions:', err);
      }

      // 2. Fetch Profile Metadata
      let profile = {};
      try {
        const profileResult = await db.query(
          'SELECT phone_number, profile_picture FROM user_profiles WHERE user_id = $1',
          [user.id]
        );
        if (profileResult.rows.length > 0) {
          profile = profileResult.rows[0];
        }
      } catch (err) {
        console.error('Error fetching user profile:', err);
      }

      const token = jwt.sign(
        {
          id: user.id,
          email: user.email,
          name: user.name,
          role: user.role,
          department: user.department,
          tower: user.tower,
          permissions
        },
        process.env.JWT_SECRET,
        { expiresIn: '7d' }
      );

      const { password: _, ...userWithoutPassword } = user;
      return res.json({
        token,
        user: {
          ...userWithoutPassword,
          permissions,
          profile
        }
      });
    } catch (err) {
      next(err);
    }
  }

  async updateProfile(req, res, next) {
    try {
      const { phone_number, profile_picture } = req.body;
      const userId = req.user.id;

      const result = await db.query(
        `INSERT INTO user_profiles (user_id, phone_number, profile_picture)
         VALUES ($1, $2, $3)
         ON CONFLICT (user_id) DO UPDATE 
         SET phone_number = EXCLUDED.phone_number, profile_picture = EXCLUDED.profile_picture
         RETURNING *`,
        [userId, phone_number || null, profile_picture || null]
      );

      return res.json({
        message: 'Profile updated successfully',
        profile: result.rows[0]
      });
    } catch (err) {
      next(err);
    }
  }
}

module.exports = new AuthController();
