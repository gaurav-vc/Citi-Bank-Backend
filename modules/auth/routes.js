const express = require('express');
const router = express.Router();
const controller = require('./controller');
const verifyToken = require('../../middleware/verifyToken');

router.post('/register', controller.register);
router.post('/login', controller.login);
router.patch('/profile', verifyToken, controller.updateProfile);

module.exports = router;
