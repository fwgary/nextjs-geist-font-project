# Discord Bot & Dashboard Implementation Plan

## Table of Contents

1. [Discord OAuth2 Setup Guide](#discord-oauth2-setup-guide)
2. [Overall Architecture Overview](#overall-architecture-overview)
3. [Part 1: Python Discord Bot](#part-1-python-discord-bot)
4. [Part 2: Next.js Dashboard](#part-2-nextjs-dashboard)
5. [Part 3: Integration, Testing, and Deployment](#part-3-integration-testing-and-deployment)

---

## Discord OAuth2 Setup Guide

### Step 1: Create Discord Application
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Name your application (e.g., "Security Bot Dashboard")
4. Click "Create"

### Step 2: Configure OAuth2 Settings
1. In your application, go to "OAuth2" → "General"
2. Add Redirect URIs:
   - For local development: `http://localhost:8000/api/auth/callback`
   - For production: `https://yourdomain.com/api/auth/callback`
3. Copy your **Client ID** and **Client Secret** (keep these secure!)

### Step 3: Set Bot Permissions
1. Go to "OAuth2" → "URL Generator"
2. Select scopes:
   - `identify` (to get user info)
   - `guilds` (to see what servers user is in)
   - `guilds.members.read` (to check user roles)
3. Copy the generated URL for later use

### Step 4: Configure Bot Settings
1. Go to "Bot" section
2. Copy your **Bot Token** (you already have this: ``)
3. Enable these Privileged Gateway Intents:
   - Message Content Intent
   - Server Members Intent
   - Presence Intent

### Step 5: Environment Variables Setup
Create a `.env.local` file in your project root with:
```env
# Discord Bot
DISCORD_TOKEN=
LOG_CHANNEL_ID=your_log_channel_id_here

# Discord OAuth2 for Dashboard
DISCORD_CLIENT_ID=your_client_id_here
DISCORD_CLIENT_SECRET=your_client_secret_here
NEXTAUTH_URL=http://localhost:8000
NEXTAUTH_SECRET=your_random_secret_key_here

# Database (for storing configurations)
DATABASE_URL=sqlite:./data/bot.db
```

### Step 6: Windows Local Hosting Setup
1. **Install Python 3.9+**: Download from [python.org](https://python.org)
2. **Install Node.js 18+**: Download from [nodejs.org](https://nodejs.org)
3. **Open Command Prompt as Administrator**
4. **Navigate to your project directory**
5. **Install dependencies** (we'll handle this in implementation)

---

## Overall Architecture Overview

- **Discord Bot (Python):** Handles moderation, logging, whitelist system
- **Web Dashboard (Next.js):** Configuration interface with Discord OAuth2 authentication
- **SQLite Database:** Stores configurations, whitelist data, and settings
- **File System:** Organized log storage by date and type

---

## Part 1: Python Discord Bot

### Directory Structure
```
bot/
├── bot.py                 # Main entry point
├── config.py             # Configuration loader
├── requirements.txt      # Python dependencies
├── database.py           # SQLite database setup
├── cogs/
│   ├── __init__.py
│   ├── moderation.py     # Moderation commands
│   ├── whitelist.py      # Whitelist system
│   └── logging_cog.py    # Logging functionality
├── utils/
│   ├── __init__.py
│   ├── file_utils.py     # File operations
│   ├── embed_utils.py    # Discord embed helpers
│   └── permissions.py    # Permission checking
└── data/
    ├── bot.db            # SQLite database
    └── logs/             # Log files directory
```

### Core Features Implementation

#### 1. Bot Configuration (config.py)
- Load environment variables
- Database connection setup
- Channel and role ID management

#### 2. Main Bot (bot.py)
- Initialize bot with both prefix and slash commands
- Load all cogs
- Event handlers for startup and errors

#### 3. Moderation Cog (cogs/moderation.py)
- **Message Sniping**: Store and retrieve deleted messages
- **Voice Channel Dragging**: Move users between voice channels
- **NSFW Channel Management**: Mark channels as NSFW
- **Role/Channel Management**: Server administration tools

#### 4. Whitelist System (cogs/whitelist.py)
- User and role-based permissions
- Command restriction enforcement
- Dynamic whitelist management

#### 5. Logging System (cogs/logging_cog.py)
- Console logging with file output
- Command usage tracking
- Deleted message logging
- Discord embed notifications
- Organized file structure: `logs/YYYY-MM-DD/[console|commands|deleted]/`

---

## Part 2: Next.js Dashboard

### Directory Structure
```
src/app/
├── layout.tsx            # Root layout
├── page.tsx             # Landing page
├── dashboard/
│   ├── layout.tsx       # Dashboard layout with auth
│   ├── page.tsx         # Dashboard home
│   ├── config/
│   │   └── page.tsx     # Configuration management
│   ├── logs/
│   │   └── page.tsx     # Log viewer
│   └── users/
│       └── page.tsx     # User management
├── api/
│   ├── auth/
│   │   └── [...nextauth]/
│   │       └── route.ts # NextAuth configuration
│   ├── bot/
│   │   ├── config/
│   │   │   └── route.ts # Bot configuration API
│   │   ├── logs/
│   │   │   └── route.ts # Logs API
│   │   └── whitelist/
│   │       └── route.ts # Whitelist management API
│   └── discord/
│       └── guilds/
│           └── route.ts # Discord guild info API
└── components/
    ├── dashboard/
    │   ├── Sidebar.tsx   # Navigation sidebar
    │   ├── ConfigForm.tsx # Configuration forms
    │   ├── LogViewer.tsx  # Log display component
    │   └── UserManager.tsx # User management
    └── auth/
        └── AuthProvider.tsx # Authentication wrapper
```

### Dashboard Features

#### 1. Authentication System
- Discord OAuth2 integration using NextAuth.js
- Role-based access control
- Session management

#### 2. Configuration Management
- Whitelist user/role management
- Module enable/disable toggles
- Permission level settings
- Real-time configuration updates

#### 3. Log Viewer
- Date-based log filtering
- Log type categorization
- Search functionality
- Export capabilities

#### 4. User Management
- View server members
- Assign dashboard permissions
- Role management interface

---

## Part 3: Implementation Steps

### Phase 1: Bot Development
1. Set up Python environment and dependencies
2. Create database schema and connection
3. Implement core bot functionality
4. Add moderation commands
5. Implement whitelist system
6. Set up comprehensive logging
7. Test all bot features

### Phase 2: Dashboard Development
1. Set up NextAuth.js with Discord OAuth2
2. Create dashboard layout and navigation
3. Implement configuration pages
4. Build log viewer interface
5. Add user management features
6. Create API endpoints for bot communication
7. Test dashboard functionality

### Phase 3: Integration & Testing
1. Connect dashboard to bot database
2. Test real-time configuration updates
3. Verify authentication and permissions
4. Test all moderation features
5. Validate logging system
6. Performance testing
7. Security audit

### Phase 4: Deployment Preparation
1. Environment configuration for production
2. Database migration scripts
3. Error handling and monitoring
4. Backup and recovery procedures
5. Documentation and user guides

---

## Security Considerations

### Bot Security
- Secure token storage
- Permission validation
- Rate limiting
- Input sanitization
- Error handling without information disclosure

### Dashboard Security
- OAuth2 implementation
- CSRF protection
- Session security
- API endpoint authentication
- Role-based access control

### Database Security
- SQL injection prevention
- Data encryption for sensitive information
- Regular backups
- Access logging

---

## File Dependencies Checklist

### Critical Files to Create:
- [ ] `.env.local` - Environment variables
- [ ] `bot/requirements.txt` - Python dependencies
- [ ] `bot/bot.py` - Main bot file
- [ ] `bot/config.py` - Configuration management
- [ ] `bot/database.py` - Database setup
- [ ] All cog files in `bot/cogs/`
- [ ] All utility files in `bot/utils/`
- [ ] Dashboard pages in `src/app/dashboard/`
- [ ] API routes in `src/app/api/`
- [ ] Authentication components
- [ ] UI components for dashboard

### Dependencies to Install:
**Python (bot/):**
- discord.py
- python-dotenv
- sqlite3 (built-in)
- aiofiles
- asyncio

**Node.js (dashboard):**
- next-auth
- @next-auth/prisma-adapter (optional)
- sqlite3 or better-sqlite3
- axios or fetch for API calls

---

This plan provides a complete roadmap for implementing both the Discord bot and web dashboard with proper authentication, security, and functionality. Each phase builds upon the previous one, ensuring a robust and maintainable system.
