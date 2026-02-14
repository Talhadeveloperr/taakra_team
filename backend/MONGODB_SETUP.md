# MongoDB Setup Guide

This guide helps you set up MongoDB for the authentication system.

## Option 1: Local MongoDB (Recommended for Development)

### macOS

```bash
# Install MongoDB with Homebrew
brew tap mongodb/brew
brew install mongodb-community

# Start MongoDB service
brew services start mongodb-community

# Verify it's running
mongosh
# You should see a MongoDB connection prompt

# Stop the service (when done)
brew services stop mongodb-community
```

### Windows

1. Download [MongoDB Community Server](https://www.mongodb.com/try/download/community)
2. Run the installer
3. MongoDB will start as a service automatically
4. Open Command Prompt and test:

```bash
mongosh
```

### Linux (Ubuntu/Debian)

```bash
# Install MongoDB
sudo apt-get install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod

# Enable on startup
sudo systemctl enable mongod

# Verify
mongosh
```

### Docker (Easiest)

```bash
# Start MongoDB in Docker
docker run --name mongodb -d -p 27017:27017 mongo:latest

# Verify it's running
docker logs mongodb

# Stop MongoDB
docker stop mongodb
```

## Option 2: MongoDB Atlas (Cloud - Free Tier)

### Create a Free Cluster

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Click "Sign Up with Email"
3. Create account and verify email
4. Click "Create" to build a cluster
5. Select the free tier (M0)
6. Choose your region
7. Click "Create Cluster"

### Get Connection String

1. Click "Connect" on your cluster
2. Click "Drivers"
3. Select "Node.js" version 3.x or 4.x
4. Copy the connection string
5. Update your `.env` file

Example connection string:

```
mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/auth-system?retryWrites=true&w=majority
```

Replace:

- `username` - Your database user
- `password` - Your database password
- `cluster0.xxxxx` - Your cluster name

### Create Database User

1. In Atlas, go to "Database Access"
2. Click "Add New Database User"
3. Choose "Password" authentication
4. Set username and password
5. Grant "Read and Write to any database"
6. Click "Add User"

### Whitelist IP Address

1. In Atlas, go to "Network Access"
2. Click "Add IP Address"
3. Click "Allow Access from Anywhere" (for development)
4. OR add your specific IP address
5. Click "Confirm"

**⚠️ For production**: Use specific IP addresses, not "Anywhere"

## Using the Connection String

### Local MongoDB

```env
MONGODB_URI=mongodb://localhost:27017/auth-system
```

This assumes MongoDB is running on your machine on port 27017.

### MongoDB Atlas

```env
MONGODB_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/auth-system?retryWrites=true&w=majority
```

Update `username`, `password`, and cluster name.

## Testing the Connection

### Using mongosh (Command Line)

```bash
# Connect to local MongoDB
mongosh

# Connect to MongoDB Atlas
mongosh "mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/auth-system"

# List databases
show databases

# Use auth-system database
use auth-system

# List collections
show collections

# Exit
exit()
```

### Using Node.js

Add this test script to `backend/test-mongo.js`:

```javascript
const mongoose = require('mongoose');

const testConnection = async () => {
  try {
    await mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/auth-system');
    console.log('✅ MongoDB connected successfully!');

    // List collections
    const collections = await mongoose.connection.db.listCollections().toArray();
    console.log('Collections:', collections.map(c => c.name));

    await mongoose.connection.close();
  } catch (error) {
    console.error('❌ MongoDB connection failed:', error.message);
    process.exit(1);
  }
};

testConnection();
```

Run it:

```bash
node test-mongo.js
```

### Using Your Application

Simply start the backend:

```bash
npm run dev
```

You should see:

```
MongoDB connected
Server running on http://localhost:5000
```

## Verifying Data

### View Database in Atlas

1. Go to Atlas dashboard
2. Click "Collections"
3. Click "auth-system" database
4. You'll see the `users` collection
5. Click on "users" to view documents

### View Database Locally

```bash
mongosh

use auth-system

db.users.find()  # Show all users

db.users.findOne({ email: "john@example.com" })  # Find specific user

db.users.count()  # Count users
```

## Common Issues

### "connect ECONNREFUSED 127.0.0.1:27017"

**Problem**: MongoDB is not running

**Solution**:
- macOS: `brew services start mongodb-community`
- Windows: Check Services (mongod should be running)
- Linux: `sudo systemctl start mongod`
- Docker: `docker run -d -p 27017:27017 mongo:latest`

### "Timeout connecting to server"

**Problem**: Connection string is incorrect

**Solution**:
- Double-check `MONGODB_URI` in `.env`
- Verify MongoDB is running
- For Atlas: Check IP whitelist

### "Authentication failed"

**Problem**: Wrong username/password

**Solution**:
- For Atlas: Verify user in "Database Access"
- Check special characters in password (URL encode if needed)
- Restart the connection

### "Cannot find module 'mongodb'"

**Problem**: Dependencies not installed

**Solution**:
```bash
cd backend
npm install
```

## Backup and Restore

### MongoDB Atlas Backup

1. Go to "Backup" in cluster menu
2. Click "Backup Now" for immediate backup
3. Click restore icon to restore from backup

### Local MongoDB Backup

```bash
# Export data
mongodump --db auth-system --out ./backup

# Import data
mongorestore --db auth-system ./backup/auth-system
```

## Cleanup

### Delete All Users

```bash
mongosh

use auth-system

db.users.deleteMany({})  # Delete all users

db.users.count()  # Verify (should be 0)
```

### Reset Database

```bash
mongosh

use auth-system

db.dropDatabase()  # Delete entire database
```

## Security Best Practices

### Development

- Use local MongoDB or free Atlas tier
- Username/password not critical
- IP whitelist not essential

### Production

- Use MongoDB Atlas (or managed service)
- Create strong username/password
- Enable IP whitelist (specific IPs only)
- Enable encryption at rest
- Enable audit logging
- Regular backups enabled
- Use TLS/SSL for connections

## Performance Tips

### Indexing

MongoDB automatically indexes `_id`. For your users collection:

```javascript
// Index email for faster lookups
db.users.createIndex({ email: 1 }, { unique: true })
```

This is handled automatically by Mongoose in the User model.

### Connection Pooling

Express automatically pools MongoDB connections. No additional configuration needed.

### Query Optimization

Good queries to know:

```javascript
// Find user by email (indexed)
await User.findOne({ email: 'test@example.com' })

// Find user by ID
await User.findById(userId)

// Count documents
await User.countDocuments()

// Update user
await User.updateOne({ email: 'test@example.com' }, { name: 'New Name' })
```

## Next Steps

Once MongoDB is set up:

1. Start the backend: `npm run dev`
2. Start the frontend: `npm run dev`
3. Create a test account
4. View the user in MongoDB

You're all set! 🎉
