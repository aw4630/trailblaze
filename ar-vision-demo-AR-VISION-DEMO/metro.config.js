const { getDefaultConfig } = require('@expo/metro-config');

const defaultConfig = getDefaultConfig(__dirname);

defaultConfig.resolver.assetExts.push(
  // AR/VR assets
  'obj',
  'mtl',
  'JPG',
  'vrx',
  'hdr',
  'gltf',
  'glb',
  'bin',
  'arobject',
  'gif',
  'png',
  'jpg',
  'jpeg',
);

module.exports = defaultConfig; 