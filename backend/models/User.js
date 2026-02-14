const mongoose = require('mongoose');
const bcrypt = require('bcrypt');

const userSchema = new mongoose.Schema({
  name: {
    type: String,
    required: [true, 'Please provide a name'],
    trim: true,
  },
  email: {
    type: String,
    required: [true, 'Please provide an email'],
    unique: true,
    lowercase: true,
    match: [
      /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/,
      'Please provide a valid email',
    ],
  },
  // 1. Password is no longer "required" because Google users don't have one
  password: {
    type: String,
    required: function() {
      return !this.googleId; // Only required if NOT a Google user
    },
    minlength: 6,
    select: false,
  },
  // 2. Add Google ID to identify OAuth users
  googleId: {
    type: String,
    unique: true,
    sparse: true, // Allows multiple users to have 'null' googleId (for manual signups)
  },
  // 3. Role-Based Access Control (RBAC)
  role: {
    type: String,
    enum: ['USER', 'ADMIN'],
    default: 'USER',
  },
  // 4. University to which the user belongs
  university: {
    type: String,
    required: [true, 'Please provide a university'],
  },
  createdAt: {
    type: Date,
    default: Date.now,
  },
});

// Hash password ONLY if it exists and is modified
userSchema.pre('save', async function (next) {
  if (!this.password || !this.isModified('password')) {
    return next();
  }

  const salt = await bcrypt.genSalt(10);
  this.password = await bcrypt.hash(this.password, salt);
});

userSchema.methods.matchPassword = async function (enteredPassword) {
  // Guard clause in case a Google user tries to login via manual form
  if (!this.password) return false; 
  return await bcrypt.compare(enteredPassword, this.password);
};

module.exports = mongoose.model('User', userSchema);