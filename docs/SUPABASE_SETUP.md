# Supabase Storage Setup for Triple G

## Overview
This guide explains how to set up Supabase storage bucket for project images in the Triple G application.

## Prerequisites
- Supabase account (https://supabase.com)
- Project created in Supabase

## Step 1: Create Storage Bucket

1. Go to your Supabase project dashboard
2. Navigate to **Storage** in the left sidebar
3. Click **New bucket**
4. Configure the bucket:
   - **Name**: `project-images`
   - **Public bucket**: ✓ (checked) - allows public read access
   - **File size limit**: 50MB (recommended)
   - **Allowed MIME types**: `image/*` (images only)

## Step 2: Set Bucket Policies

After creating the bucket, set up policies to control access:

### Method 1: Using Supabase Dashboard (Recommended)

1. Go to **Storage** > Click on `project-images` bucket
2. Click **Policies** tab
3. Click **New Policy** button

#### Policy 1: Public Read Access
1. Click **New Policy**
2. Select **For full customization** (or use template)
3. Fill in:
   - **Policy name**: `Public Read Access`
   - **Allowed operation**: `SELECT`
   - **Target roles**: Select `public` (for anyone) OR `authenticated` (for logged-in users only)
   - **Policy definition (USING)**: 
   ```sql
   bucket_id = 'project-images'
   ```
4. Click **Review**
5. Verify the SQL shows `TO public` (not `TO authenticated`)
6. Click **Save policy**

#### Policy 2: Authenticated Upload
1. Click **New Policy**
2. Fill in:
   - **Policy name**: `Authenticated Upload`
   - **Allowed operation**: `INSERT`
   - **Policy definition**:
   ```sql
   (bucket_id = 'project-images')
   ```
   - **WITH CHECK expression**:
   ```sql
   (bucket_id = 'project-images')
   ```
3. Click **Review** then **Save policy**

#### Policy 3: Authenticated Delete
1. Click **New Policy**
2. Fill in:
   - **Policy name**: `Authenticated Delete`
   - **Allowed operation**: `DELETE`
   - **Policy definition**:
   ```sql
   (bucket_id = 'project-images')
   ```
3. Click **Review** then **Save policy**

### Method 2: Using SQL Editor

1. Go to **SQL Editor** in Supabase dashboard
2. Click **New query**
3. Paste and run each policy:

```sql
-- Policy 1: Public Read Access
CREATE POLICY "Public Read Access"
ON storage.objects FOR SELECT
USING ( bucket_id = 'project-images' );

-- Policy 2: Authenticated Upload
CREATE POLICY "Authenticated Upload"
ON storage.objects FOR INSERT
WITH CHECK ( bucket_id = 'project-images' );

-- Policy 3: Authenticated Delete
CREATE POLICY "Authenticated Delete"
ON storage.objects FOR DELETE
USING ( bucket_id = 'project-images' );
```

4. Click **Run** to execute

### Verify Policies

After creating policies, verify them:
1. Go to **Storage** > `project-images` > **Policies** tab
2. You should see 3 policies listed:
   - ✓ Public Read Access (SELECT)
   - ✓ Authenticated Upload (INSERT)
   - ✓ Authenticated Delete (DELETE)

## Step 3: Get Supabase Credentials

1. Go to **Project Settings** > **API**
2. Copy the following values:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon/public key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

## Step 4: Configure Environment Variables

Add these to your `.env` file:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_BUCKET=project-images
```

## Step 5: Install Required Package

```bash
pip install requests
```

## Step 6: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

## Usage

### Upload Project Image
When creating or editing a project, simply upload an image through the form. The image will automatically be stored in Supabase.

### Access Image URL
```python
project = Project.objects.get(id=1)
image_url = project.image.url  # Returns public Supabase URL
```

### Delete Image
```python
project.image.delete()  # Removes from Supabase bucket
```

## File Structure

```
project_images/
├── project_1_image.jpg
├── project_2_image.png
└── ...
```

## Security Notes

1. **Public Bucket**: Images are publicly accessible via URL
2. **Upload Restrictions**: Only authenticated Django users can upload
3. **File Validation**: Django validates file types and sizes
4. **CORS**: Supabase automatically handles CORS for public buckets

## Troubleshooting

### Issue: Upload fails with 401 error
**Solution**: Check that SUPABASE_KEY is correct and has proper permissions

### Issue: Images not displaying
**Solution**: Verify bucket is set to public and policies are configured

### Issue: Connection timeout
**Solution**: Check SUPABASE_URL is correct and accessible

## Alternative: Keep Local Storage

To use local storage instead of Supabase, modify `site_diary/models.py`:

```python
# Change this:
image = models.ImageField(upload_to='project_images/', storage=SupabaseStorage(), null=True, blank=True)

# To this:
image = models.ImageField(upload_to='project_images/', null=True, blank=True)
```

## Bucket Configuration Summary

| Setting | Value |
|---------|-------|
| Bucket Name | project-images |
| Public Access | Yes |
| Max File Size | 50MB |
| Allowed Types | image/* |
| Upload Auth | Required |
| Read Access | Public |

## Next Steps

1. Create the bucket in Supabase dashboard
2. Set up policies
3. Add credentials to .env
4. Test upload functionality
5. Monitor storage usage in Supabase dashboard

For more information, visit: https://supabase.com/docs/guides/storage
