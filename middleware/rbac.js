const requirePermission = (featureKey, action) => {
  return (req, res, next) => {
    // Verify user exists
    if (!req.user) {
      return res.status(401).json({
        error: 'Unauthorized: User not found',
      });
    }

    // TEMP DEVELOPMENT BYPASS
    // TODO: Re-enable strict RBAC after stabilization

    console.log(
      `[RBAC BYPASS] ${req.user?.email || 'Unknown User'} -> ${featureKey}:${action}`
    );

    return next();

    /*
    // STRICT RBAC VERSION (RESTORE LATER)

    const permissions = req.user.permissions || {};
    const featurePermissions = permissions[featureKey];

    if (
      featurePermissions &&
      featurePermissions[action] === true
    ) {
      return next();
    }

    return res.status(403).json({
      error: `Forbidden: Requires '${action}' permission for '${featureKey}'`,
    });
    */
  };
};

module.exports = requirePermission;