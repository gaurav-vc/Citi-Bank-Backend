const express = require('express');
const router = express.Router();
const controller = require('./controller');
const verifyToken = require('../../middleware/verifyToken');
const requireRole = require('../../middleware/requireRole');

router.get('/pending', verifyToken, controller.getPendingApprovals);
router.post('/action', verifyToken, controller.actionStep);
router.post('/escalate', verifyToken, requireRole('procurement_manager', 'cxo'), controller.escalateOverdueSteps);

module.exports = router;
