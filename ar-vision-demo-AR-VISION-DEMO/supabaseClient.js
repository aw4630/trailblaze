import { createClient } from '@supabase/supabase-js';
import * as FileSystem from 'expo-file-system';
import { decode } from 'base64-arraybuffer';
import { SUPABASE_URL, SUPABASE_KEY } from './environment';

// Initialize Supabase client
const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

/**
 * Upload an image to Supabase Storage
 * @param {string} uri - Local URI of the image
 * @param {string} landmarkName - Name of the landmark detected
 * @param {object} location - Location coordinates object
 * @returns {Promise<object>} Upload result with URL
 */
export const uploadLandmarkImage = async (uri, landmarkName, location) => {
  try {
    // Get the file extension
    const fileExt = uri.split('.').pop();
    
    // Create a unique file name
    const fileName = `${Date.now()}_${landmarkName.replace(/[^a-zA-Z0-9]/g, '_')}.${fileExt}`;
    
    // Read the file as base64
    const base64File = await FileSystem.readAsStringAsync(uri, {
      encoding: FileSystem.EncodingType.Base64,
    });
    
    // Convert base64 to ArrayBuffer (required by Supabase)
    const fileBuffer = decode(base64File);
    
    // Upload to Supabase Storage
    const { data, error } = await supabase.storage
      .from('landmarks')  // Bucket name - create this in your Supabase dashboard
      .upload(fileName, fileBuffer, {
        contentType: `image/${fileExt}`,
      });
    
    if (error) {
      throw new Error(`Storage error: ${error.message}`);
    }
    
    // Get the public URL
    const { data: urlData } = supabase.storage
      .from('landmarks')
      .getPublicUrl(fileName);
    
    // Save metadata to database
    const { error: dbError } = await supabase
      .from('landmark_records')  // Table name - create this in your Supabase dashboard
      .insert({
        image_url: urlData.publicUrl,
        landmark_name: landmarkName,
        latitude: location?.coords?.latitude || null,
        longitude: location?.coords?.longitude || null,
        captured_at: new Date().toISOString(),
      });
    
    if (dbError) {
      throw new Error(`Database error: ${dbError.message}`);
    }
    
    return {
      success: true,
      url: urlData.publicUrl,
      fileName,
    };
    
  } catch (error) {
    console.error('Error uploading to Supabase:', error);
    throw error;
  }
};

/**
 * Fetch all saved landmarks
 * @returns {Promise<Array>} Array of landmark records
 */
export const getLandmarks = async () => {
  const { data, error } = await supabase
    .from('landmark_records')
    .select('*')
    .order('captured_at', { ascending: false });
    
  if (error) {
    throw new Error(`Fetch error: ${error.message}`);
  }
  
  return data;
};

export default supabase; 