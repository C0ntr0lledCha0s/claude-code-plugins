/**
 * Custom version updater for marketplace.json
 * Used by standard-version to update the marketplace metadata version
 */

const fs = require('fs');

module.exports.readVersion = function (contents) {
  const marketplace = JSON.parse(contents);
  return marketplace.metadata?.version || '1.0.0';
};

module.exports.writeVersion = function (contents, version) {
  const marketplace = JSON.parse(contents);

  // Update the metadata version
  if (!marketplace.metadata) {
    marketplace.metadata = {};
  }
  marketplace.metadata.version = version;

  // Update the lastUpdated timestamp
  marketplace.metadata.lastUpdated = new Date().toISOString().split('T')[0];

  return JSON.stringify(marketplace, null, 2) + '\n';
};
