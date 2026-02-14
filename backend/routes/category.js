const express = require('express');
const { protect, authorize } = require('../middleware/auth');
// const { pool, poolConnect } = require('../config/sql');

const router = express.Router();

/* ADMIN: Create Category */
router.post('/', protect, authorize('ADMIN'), async (req, res) => {
  
    const pool = req.app.locals.sqlPool;
  const { category_id, name, description } = req.body;

  await pool.request()
    .input('category_id', category_id)
    .input('name', name)
    .input('description', description)
    .query(`
      INSERT INTO categories (category_id, name, description)
      VALUES (@category_id, @name, @description)
    `);

  res.json({ success: true });
});

/* USER: Get All Categories */
router.get('/', async (req, res) => {

    const pool = req.app.locals.sqlPool;
  const result = await pool.request()
    .query(`SELECT * FROM categories`);

  res.json(result.recordset);
});

module.exports = router;
