# Replit Deployment Guide

This guide explains how to deploy the AI Development Assistant on Replit.

## 🚀 Quick Start

1. **Fork/Import** this project to Replit
2. **Set Environment Variables** in Replit Secrets
3. **Run the project** - it will automatically start both backend and frontend

## 📋 Prerequisites

- Replit account
- MongoDB Atlas database (free tier available)
- Claude API key from Anthropic

## 🔧 Environment Variables Setup

In Replit, go to **Tools → Secrets** and add these variables:

### Required Variables:
```
ANTHROPIC_API_KEY=your_claude_api_key_here
MONGODB_URI=your_mongodb_atlas_connection_string
```

### Optional Variables:
```
CORS_ORIGINS=https://your-custom-domain.com
```

## 🏗 Project Structure for Replit

```
├── .replit              # Replit configuration
├── replit.nix           # Nix packages
├── run.sh               # Main deployment script
├── backend/             # FastAPI backend
├── frontend/            # Next.js frontend
└── REPLIT_DEPLOYMENT.md # This file
```

## 🔄 How It Works

### Deployment Script (`run.sh`)
1. **Installs Python dependencies** for backend
2. **Installs Node.js dependencies** for frontend
3. **Builds Next.js frontend** for production
4. **Starts FastAPI backend** on port 8000
5. **Starts Next.js frontend** on port 3000

### API Configuration
- **Frontend**: Uses relative URLs for API calls (same-origin)
- **Backend**: Configured with CORS for Replit domain
- **Communication**: Frontend proxies requests to backend

## 🌐 Accessing Your App

Once deployed, your app will be available at:
- **Frontend**: `https://your-repl-name.your-username.repl.co`
- **Backend API**: `https://your-repl-name.your-username.repl.co:8000`

## 🔍 Troubleshooting

### Common Issues:

1. **"Module not found" errors**
   - Check that all dependencies are in `requirements.txt` and `package.json`
   - Ensure `replit.nix` includes required system packages

2. **CORS errors**
   - Verify environment variables are set correctly
   - Check that CORS origins include your Replit domain

3. **Database connection issues**
   - Ensure MongoDB Atlas connection string is correct
   - Check network access settings in MongoDB Atlas

4. **Port conflicts**
   - Replit automatically assigns ports
   - The script uses ports 8000 (backend) and 3000 (frontend)

### Debugging:

1. **Check logs** in Replit console
2. **Test backend directly** by visiting the API endpoints
3. **Verify environment variables** are loaded correctly

## 🔧 Customization

### Adding New Dependencies:

**Python (Backend):**
- Add to `backend/requirements.txt`
- Update `replit.nix` if system packages needed

**Node.js (Frontend):**
- Add to `frontend/package.json`
- Run `npm install` in the deployment script

### Modifying Ports:
- Update `run.sh` with new port numbers
- Update CORS configuration in `backend/main.py`
- Update API configuration in `frontend/src/lib/api-config.ts`

## 📊 Monitoring

- **Replit Analytics**: Built-in usage statistics
- **Application Logs**: Available in Replit console
- **Health Check**: Visit `/health` endpoint on backend

## 🔒 Security Notes

- **Environment Variables**: Never commit API keys to code
- **CORS**: Configured for Replit domains only
- **Database**: Use MongoDB Atlas with proper authentication
- **API Keys**: Store securely in Replit Secrets

## 🚀 Production Considerations

For production deployment:
1. **Upgrade Replit plan** for better performance
2. **Use custom domain** if needed
3. **Set up monitoring** and logging
4. **Configure backups** for MongoDB data
5. **Implement rate limiting** for API endpoints

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review Replit documentation
3. Check application logs for error messages
4. Verify all environment variables are set correctly 