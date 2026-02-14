// utils/userHelpers.js
const { v4: uuidv4 } = require('uuid');
const { setupUserDatabase } = require('../database/main');
const User = require('../models/User');

exports.initializeNewUser = async (userData) => {
  // 1. Generate clean UUID for SQL
  const rawUuid = uuidv4().replace(/-/g, '_');
  const newUuid = `u${rawUuid}`;

  // 2. Create User in MongoDB
  const user = await User.create({
    ...userData,
    uuid: newUuid,
    role: 'USER' // Default role for Takraa participants
  });

  // 3. Trigger MySQL Database Creation for this specific user
  await setupUserDatabase(newUuid);

  return user;
};