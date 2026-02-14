const express = require('express');
const { protect, authorize } = require('../middleware/auth');

const router = express.Router();

/* ADMIN: Create Competition */
router.post('/', protect, authorize('ADMIN'), async (req, res) => {
    try {
        const pool = req.app.locals.sqlPool;
        const {
            category_id,
            title,
            tagline,
            description,
            rules,
            prizes,
            min_team_size,
            max_team_size,
            start_date,
            end_date,
            registration_deadline,
            status = 'upcoming'
        } = req.body;

        if (!category_id || !title) {
            return res.status(400).json({ success: false, message: "category_id and title are required" });
        }

        // Get the highest competition_id and increment by 1
        const maxIdResult = await pool.request().query(`SELECT ISNULL(MAX(competition_id), 100) AS max_id FROM competitions`);
        const newCompetitionId = maxIdResult.recordset[0].max_id + 1;

        // Insert new competition
        await pool.request()
            .input('competition_id', newCompetitionId)
            .input('category_id', category_id)
            .input('title', title)
            .input('tagline', tagline || null)
            .input('description', description || null)
            .input('rules', rules || null)
            .input('prizes', prizes || null)
            .input('min_team_size', min_team_size || null)
            .input('max_team_size', max_team_size || null)
            .input('start_date', start_date || null)
            .input('end_date', end_date || null)
            .input('registration_deadline', registration_deadline || null)
            .input('status', status)
            .query(`
                INSERT INTO competitions (
                    competition_id, category_id, title, tagline, description,
                    rules, prizes, min_team_size, max_team_size,
                    start_date, end_date, registration_deadline, status, created_at
                )
                VALUES (
                    @competition_id, @category_id, @title, @tagline, @description,
                    @rules, @prizes, @min_team_size, @max_team_size,
                    @start_date, @end_date, @registration_deadline, @status, GETDATE()
                )
            `);

        res.json({ success: true, message: "Competition created", competition_id: newCompetitionId });
    } catch (err) {
        console.error(err);
        res.status(500).json({ success: false, message: err.message });
    }
});

/* PUBLIC: Get All Competitions */
router.get('/', async (req, res) => {
    try {
        const pool = req.app.locals.sqlPool;
        const result = await pool.request().query(`
            SELECT c.*, cat.name AS category_name
            FROM competitions c
            JOIN categories cat ON c.category_id = cat.category_id
            ORDER BY c.start_date ASC
        `);
        res.json({ success: true, competitions: result.recordset });
    } catch (err) {
        console.error(err);
        res.status(500).json({ success: false, message: err.message });
    }
});

/* PUBLIC: Competition Detail */
router.get('/:id', async (req, res) => {
    try {
        const pool = req.app.locals.sqlPool;
        const result = await pool.request()
            .input('id', req.params.id)
            .query(`
                SELECT c.*, cat.name AS category_name
                FROM competitions c
                JOIN categories cat ON c.category_id = cat.category_id
                WHERE c.competition_id = @id
            `);

        if (result.recordset.length === 0) {
            return res.status(404).json({ success: false, message: "Competition not found" });
        }

        res.json({ success: true, competition: result.recordset[0] });
    } catch (err) {
        console.error(err);
        res.status(500).json({ success: false, message: err.message });
    }
});

module.exports = router;
