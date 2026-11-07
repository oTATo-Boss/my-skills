// Minimal DOM boundary captured from Flow's /asb/ thumbnails (2026-11-02).
const fs = require('node:fs');
const {source, ambiguous, duplicateNames, captureClick, hideGridAfterFirstResolution} = JSON.parse(fs.readFileSync(0, 'utf8'));
const media = 'cd82b996-cc81-40f8-bd2a-fee0f96556f0';
const asb = 'https://flow.google.com/asb/opaque-reference';
const image = (src, id = null) => ({
  src, currentSrc: src, naturalWidth: 896, naturalHeight: 1200,
  getAttribute: name => name === 'data-media-id' ? id : null,
});
const grid = [image(asb + '=s512-rw', media)];
if (ambiguous) grid.push(image(asb + '=s512-rw', '11111111-1111-4111-8111-111111111111'));
const thumbnail = image(asb + '=s3200-rw');
const legacy = image('https://flow-content.google/image/22222222-2222-4222-8222-222222222222?test=1');
const clicked = [];
const option = im => ({
  querySelector: s => s === '.asset-title' ? {textContent: 'reference.jpg'} : im,
  getClientRects: () => [1],
  click: () => clicked.push(im === thumbnail ? media : '22222222-2222-4222-8222-222222222222'),
});
const options = [option(thumbnail)];
if (duplicateNames) options.push(option(legacy));
global.location = {origin: 'https://flow.google.com'};
global.document = {
  images: [...grid, legacy],
  querySelectorAll(selector) {
    if (selector === 'flow-grid-tile-container img[data-media-id]') return grid;
    if (selector === '[role=option]') return options;
    if (selector.startsWith('button[aria-label=')) return [{
      getClientRects: () => [1], getAttribute: () => 'false', querySelector: () => thumbnail,
    }];
    throw new Error('Unexpected DOM selector: ' + selector);
  },
};
const read = eval('(' + source + ')');
if (hideGridAfterFirstResolution) { read(); grid.length = 0; }
const result = read();
process.stdout.write(JSON.stringify(captureClick ? {result, clicked} : result));
