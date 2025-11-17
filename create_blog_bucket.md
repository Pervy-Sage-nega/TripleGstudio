# Create blog-images Bucket in Supabase

## Steps to Fix the Blog Image Upload Issue

The error shows that the `blog-images` bucket doesn't exist in your Supabase storage.

### 1. Go to Supabase Dashboard
- Visit: https://supabase.com/dashboard
- Select your project: `zwxyokgkomrvwcddgbli`

### 2. Create the blog-images Bucket
- Go to **Storage** in the left sidebar
- Click **New bucket**
- Bucket name: `blog-images`
- Make it **Public** (check the public checkbox)
- Click **Create bucket**

### 3. Verify Other Buckets Exist
Make sure these buckets also exist and are public:
- `admin-profiles` ✅ (already working)
- `sitemanager-profiles` ✅ (already working) 
- `client-profiles` ✅ (already working)
- `project-images` ✅ (already working)
- `blog-images` ❌ (needs to be created)

### 4. Test After Creation
After creating the bucket, try uploading a blog post with a featured image again.

## Current Status
- **Working**: Profile pictures for all user types
- **Working**: Portfolio project images  
- **Issue**: Blog images (bucket missing)
- **Debug**: Enhanced logging shows exact error