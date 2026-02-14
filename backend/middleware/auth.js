const jwt = require('jsonwebtoken');

// 1. Authentication Middleware: Verifies "Who you are"
exports.protect = async (req, res, next) => {
  let token;

  if (req.cookies && req.cookies.auth_token) {
    token = req.cookies.auth_token;
  }

  if (!token) {
    return res.status(401).json({ success: false, message: 'Not authorized to access this route' });
  }

  try {
    // Verify token
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    
    // Now req.user will contain { id: '...', role: 'ADMIN' } 
    // This works for both Google OAuth and Manual JWT users
    req.user = decoded; 
    next();
  } catch (error) {
    return res.status(401).json({ success: false, message: 'Token is invalid or expired' });
  }
};

// 2. Authorization Middleware: Verifies "What you can do"
// Pass the allowed roles as arguments, e.g., authorize('ADMIN')
exports.authorize = (...roles) => {
  return (req, res, next) => {
    if (!req.user || !roles.includes(req.user.role)) {
      return res.status(403).json({
        success: false,
        message: `User role '${req.user?.role}' is not authorized to access this route`,
      });
    }
    next();
  };
};