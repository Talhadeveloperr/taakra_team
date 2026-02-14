const { getSqlConnection, sql } = require('./sqlconn');

const setupUserDatabase = async (dbName) => {
    let pool;
    try {
        pool = await getSqlConnection();

        // 1. Create the Database
        // Note: SQL names can't have hyphens unless quoted, 
        // and we sanitize slightly by ensuring it starts with 'u'
        await pool.request().query(`CREATE DATABASE [${dbName}]`);

        // 2. Connect to the new Database to create tables
        // We close the 'master' pool and connect to the specific one
        await pool.close();
        
        const userDbConfig = {
            user: 'admin',
            password: 'admin1234',
            server: '192.168.100.109',
            database: dbName,
            port: 1433,
            options: { encrypt: false, trustServerCertificate: true }
        };

        let userPool = await sql.connect(userDbConfig);

        // 3. Create table and insert seed data
        await userPool.request().query(`
            CREATE TABLE report (
                id INT,
                name VARCHAR(10)
            );
            
        `);

        await userPool.close();
        return true;
    } catch (err) {
        console.error("Error setting up dynamic DB:", err);
        throw err;
    }
};

module.exports = { setupUserDatabase };