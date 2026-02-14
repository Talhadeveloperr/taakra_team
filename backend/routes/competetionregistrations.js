const express = require('express');
const { protect, authorize } = require('../middleware/auth');

const router = express.Router();

/* USER: Register for Competition */
router.post('/', protect, async (req, res) => {
    try {
        const pool = req.app.locals.sqlPool;
        const { competition_id, team_name } = req.body;

        if (!competition_id || !team_name) {
            return res.status(400).json({ success: false, message: "Please provide competition_id and team_name" });
        }

        // Use user UUID from JWT (stored in req.user.uuid)
        const user_id = req.user.uuid;

        // Check if user already registered
        const existing = await pool.request()
            .input('competition_id', competition_id)
            .input('user_id', user_id)
            .query(`
                SELECT 1 FROM registrations
                WHERE competition_id = @competition_id AND user_id = @user_id
            `);

        if (existing.recordset.length > 0) {
            return res.status(400).json({ success: false, message: "Already registered for this competition" });
        }

        // Insert registration
        await pool.request()
            .input('competition_id', competition_id)
            .input('user_id', user_id)
            .input('team_name', team_name)
            .query(`
                INSERT INTO registrations (competition_id, user_id, team_name)
                VALUES (@competition_id, @user_id, @team_name)
            `);

        res.json({ success: true, message: "Registered successfully" });
    } catch (err) {
        console.error(err);
        res.status(500).json({ success: false, message: err.message });
    }
});

/* USER: My Registrations */
router.get('/my', protect, async (req, res) => {
    try {
        const pool = req.app.locals.sqlPool;
        const user_id = req.user.uuid;

        const result = await pool.request()
            .input('user_id', user_id)
            .query(`
                SELECT r.registration_id, c.title, r.team_name, r.status, r.registered_at
                FROM registrations r
                JOIN competitions c ON r.competition_id = c.competition_id
                WHERE r.user_id = @user_id
                ORDER BY r.registered_at DESC
            `);

        res.json({ success: true, registrations: result.recordset });
    } catch (err) {
        console.error(err);
        res.status(500).json({ success: false, message: err.message });
    }
});

/* ADMIN: Approve Registration */
router.put('/:id/approve', protect, authorize('ADMIN'), async (req, res) => {
    try {
        const pool = req.app.locals.sqlPool;
        const registration_id = req.params.id;
        const admin_id = req.user.uuid;

        await pool.request()
            .input('id', registration_id)
            .input('admin_id', admin_id)
            .query(`
                UPDATE registrations
                SET status = 'approved',
                    reviewed_at = GETDATE(),
                    reviewed_by = @admin_id
                WHERE registration_id = @id
            `);

        res.json({ success: true, message: "Registration approved" });
    } catch (err) {
        console.error(err);
        res.status(500).json({ success: false, message: err.message });
    }
});

/* ADMIN: Get All Pending Registrations */
router.get('/pending', protect, authorize('ADMIN'), async (req, res) => {
    try {
        const pool = req.app.locals.sqlPool;

        const result = await pool.request().query(`
            SELECT r.registration_id, u.full_name, u.email, c.title, r.team_name, r.registered_at
            FROM registrations r
            JOIN users u ON r.user_id = u.user_id
            JOIN competitions c ON r.competition_id = c.competition_id
            WHERE r.status = 'pending'
            ORDER BY r.registered_at ASC
        `);

        res.json({ success: true, pending: result.recordset });
    } catch (err) {
        console.error(err);
        res.status(500).json({ success: false, message: err.message });
    }
});

/* ADMIN: Create a New Competition (with manual ID increment) */
router.post('/competition', protect, authorize('ADMIN'), async (req, res) => {
    try {
        const pool = req.app.locals.sqlPool;
        const { category_id, title, tagline, description, rules, prizes, min_team_size, max_team_size, start_date, end_date, registration_deadline } = req.body;

        // Get max competition_id and increment
        const maxIdResult = await pool.request().query(`SELECT ISNULL(MAX(competition_id), 100) AS max_id FROM competitions`);
        const newCompetitionId = maxIdResult.recordset[0].max_id + 1;

        await pool.request()
            .input('competition_id', newCompetitionId)
            .input('category_id', category_id)
            .input('title', title)
            .input('tagline', tagline)
            .input('description', description)
            .input('rules', rules)
            .input('prizes', prizes)
            .input('min_team_size', min_team_size)
            .input('max_team_size', max_team_size)
            .input('start_date', start_date)
            .input('end_date', end_date)
            .input('registration_deadline', registration_deadline)
            .query(`
                INSERT INTO competitions (
                    competition_id, category_id, title, tagline, description, rules, prizes, min_team_size, max_team_size, start_date, end_date, registration_deadline
                ) VALUES (
                    @competition_id, @category_id, @title, @tagline, @description, @rules, @prizes, @min_team_size, @max_team_size, @start_date, @end_date, @registration_deadline
                )
            `);

        res.json({ success: true, message: "Competition created", competition_id: newCompetitionId });
    } catch (err) {
        console.error(err);
        res.status(500).json({ success: false, message: err.message });
    }
});

module.exports = router;
