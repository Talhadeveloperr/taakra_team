const express = require('express');
const { protect, authorize } = require('../middleware/auth');
// const { pool, poolConnect } = require('../config/sql');

const router = express.Router();

router.get('/analytics/registrations-per-day',
  protect,
  authorize('ADMIN'),
  async (req, res) => {

    const pool = req.app.locals.sqlPool;

    const result = await pool.request().query(`
      SELECT CAST(registered_at AS DATE) AS date,
             COUNT(*) AS total
      FROM registrations
      GROUP BY CAST(registered_at AS DATE)
      ORDER BY date
    `);

    res.json(result.recordset);
  }
);

module.exports = router;
