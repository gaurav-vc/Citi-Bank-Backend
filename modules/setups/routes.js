const express = require('express');
const router = express.Router();
const controller = require('./controller');
const verifyToken = require('../../middleware/verifyToken');
const requireRole = require('../../middleware/requireRole'); // Simple role fallback check

router.get('/roles', verifyToken, controller.getRoles);
router.get('/departments', verifyToken, controller.getDepartments);
router.post('/departments', verifyToken, requireRole('procurement_manager'), controller.createDepartment);
router.get('/organizations', verifyToken, controller.getOrganizations);
router.post('/organizations', verifyToken, requireRole('procurement_manager'), controller.createOrganization);
router.get('/sites', verifyToken, controller.getSites);
router.post('/sites', verifyToken, requireRole('procurement_manager'), controller.createSite);
router.get('/users-hierarchy', verifyToken, requireRole('procurement_manager', 'cxo'), controller.getUsersHierarchy);
router.post('/assign-user', verifyToken, requireRole('procurement_manager'), controller.assignUserHierarchy);
router.get('/modules-features', verifyToken, controller.getModulesAndFeatures);
router.get('/mappings', verifyToken, requireRole('procurement_manager', 'cxo'), controller.getMappings);
router.post('/sync-mapping', verifyToken, requireRole('procurement_manager'), controller.syncMapping);
router.post('/seed', controller.seedDefaults); // Public or admin seed trigger

module.exports = router;
