# Running Shadow AI on Replit

This guide explains how to run the Shadow AI project on Replit.

## Overview

This project consists of:

- A FastAPI backend (running on port 8000)
- A Next.js frontend (running on port 3000)

## How to Run

1. Simply click the "Run" button in Replit.
2. The script will automatically:
   - Install Python dependencies
   - Start the FastAPI backend
   - Fix Tailwind CSS configuration
   - Install and update Node.js dependencies
   - Build and start the Next.js frontend

## Accessing the Application

- Frontend: https://$REPL_SLUG.$REPL_OWNER.repl.co
- Backend API: https://$REPL_SLUG.$REPL_OWNER.repl.co:8000

## Troubleshooting

If you encounter any issues:

1. Check the backend logs:

   ```
   cat backend/backend.log
   ```
2. Check the frontend logs:

   ```
   cat frontend/frontend.log
   ```
3. Common issues:

   - If the frontend fails to build, the script will automatically try to run it in development mode instead
   - If Tailwind CSS issues persist, try manually installing it with:
     ```
     cd frontend
     npm install tailwindcss@latest postcss@latest autoprefixer@latest --save-dev
     ```

## Manual Restart

If you need to restart the application manually:

```
bash run.sh
```
