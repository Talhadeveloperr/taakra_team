const express = require('express');
const User = require('../models/User'); // MongoDB Model
const jwt = require('jsonwebtoken');
const { protect } = require('../middleware/auth');
const { v4: uuidv4 } = require('uuid');
const { OAuth2Client } = require('google-auth-library');
const sql = require('mssql');

const router = express.Router();
const client = new OAuth2Client(process.env.GOOGLE_CLIENT_ID);

// --- HELPERS ---

/**
 * Generate JWT Token with ID and Role
 */
const generateToken = (id, role) => {
  return jwt.sign({ id, role }, process.env.JWT_SECRET, {
    expiresIn: '7d',
  });
};

/**
 * Unified Cookie Setter
 */
const setCookie = (res, token) => {
  res.cookie('auth_token', token, {
    httpOnly: true,
    sameSite: process.env.NODE_ENV === 'production' ? 'strict' : 'lax',
    secure: process.env.NODE_ENV === 'production',
    maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
  });
};

/**
 * Generates a unique UUID by checking against MongoDB
 */
const generateUniqueUuid = async () => {
  let isDuplicate = true;
  let newUuid;

  while (isDuplicate) {
    newUuid = uuidv4(); // DO NOT modify format

    const existingUser = await User.findOne({ uuid: newUuid });
    if (!existingUser) {
      isDuplicate = false;
    }
  }

  return newUuid;
};


/**
 * Helper to sync user to SQL Server (taakra_db)
 */
const syncToSql = async ({ uuid, name, email, university }) => {
  try {
    const request = new sql.Request();

    await request
      .input('user_id', sql.VarChar, uuid)
      .input('full_name', sql.VarChar, name)
      .input('email', sql.VarChar, email)
      .input('university', sql.VarChar, university || null)
      .query(`
        IF NOT EXISTS (SELECT 1 FROM users WHERE email = @email)
        BEGIN
          INSERT INTO users (user_id, full_name, email, university)
          VALUES (@user_id, @full_name, @email, @university)
        END
        ELSE
        BEGIN
          UPDATE users
          SET full_name = @full_name,
              university = @university,
              user_id = @user_id
          WHERE email = @email
        END
      `);

    console.log(`✅ SQL Sync: ${name} synced successfully.`);
  } catch (err) {
    console.error("❌ SQL Sync Error:", err.message);
  }
};


// --- ROUTES ---

// @route   POST /api/auth/register
// @desc    Register a new user in both Mongo and SQL
router.post('/register', async (req, res) => {
  try {
    const { name, email, password, role , university} = req.body;

    if (!name || !email || !password) {
      return res.status(400).json({ success: false, message: 'Please provide all details' });
    }

    const existingUser = await User.findOne({ email });
    if (existingUser) {
      return res.status(400).json({ success: false, message: 'Email already registered' });
    }

    const newUuid = await generateUniqueUuid();
    const assignedRole = role || 'USER';

    // 1. Create in MongoDB
    const user = await User.create({
      name,
      email,
      password,
      uuid: newUuid,
      role: assignedRole,
      university
    });

    // 2. Sync to SQL Server
    await syncToSql({ uuid: newUuid, name, email, university});


    const token = generateToken(user._id, user.role);
    setCookie(res, token);

    res.status(201).json({
      success: true,
      user: { id: user._id, uuid: user.uuid, name: user.name, role: user.role },
    });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

// @route   POST /api/auth/login
// @desc    Standard Login
router.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    if (!email || !password) return res.status(400).json({ success: false, message: 'Provide credentials' });

    const user = await User.findOne({ email }).select('+password');
    if (!user || !(await user.matchPassword(password))) {
      return res.status(401).json({ success: false, message: 'Invalid credentials' });
    }

    const token = generateToken(user._id, user.role);
    setCookie(res, token);

    res.status(200).json({
      success: true,
      user: { id: user._id, uuid: user.uuid, name: user.name, role: user.role },
    });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

// @route   POST /api/auth/google
// @desc    Google OAuth Bridge with Dual-DB sync
router.post('/google', async (req, res) => {
  try {
    const { idToken } = req.body;
    const ticket = await client.verifyIdToken({
      idToken,
      audience: process.env.GOOGLE_CLIENT_ID,
    });

    const { email, name, sub: googleId } = ticket.getPayload();
    let user = await User.findOne({ email });

    if (!user) {
      // New Google User
      const newUuid = await generateUniqueUuid();
      const assignedRole = 'USER';

      user = await User.create({
        name,
        email,
        googleId,
        uuid: newUuid,
        role: assignedRole
      });

      // Sync new user to SQL
      await syncToSql({
        uuid: newUuid,
        name,
        email,
        university: null
      });
      
    } else {
      // Existing User: Update Google ID and Sync info to SQL
      if (!user.googleId) {
        user.googleId = googleId;
        await user.save();
      }
      await syncToSql({
        uuid: user.uuid,
        name: user.name,
        email: user.email,
        university: user.university || null
      });
      
    }

    const token = generateToken(user._id, user.role);
    setCookie(res, token);

    res.status(200).json({
      success: true,
      user: { id: user._id, uuid: user.uuid, name: user.name, role: user.role }
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ success: false, message: 'Google authentication failed' });
  }
});

// @route   POST /api/auth/logout
router.post('/logout', protect, (req, res) => {
  res.cookie('auth_token', '', {
    httpOnly: true,
    sameSite: process.env.NODE_ENV === 'production' ? 'strict' : 'lax',
    secure: process.env.NODE_ENV === 'production',
    maxAge: 0,
  });
  res.status(200).json({ success: true, message: 'Logged out successfully' });
});

// @route   GET /api/auth/me
router.get('/me', protect, async (req, res) => {
  try {
    const user = await User.findById(req.user.id);
    res.status(200).json({
      success: true,
      user: { id: user._id, name: user.name, email: user.email, role: user.role, uuid: user.uuid },
    });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

module.exports = router;