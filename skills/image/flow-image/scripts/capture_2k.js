async ({action, mediaId, projectUrl}) => {
  if (location.origin + location.pathname.replace(/\/$/, '') !== projectUrl) {
    throw new Error('The Flow project changed');
  }

  const key = Symbol.for('flow-image.2k-downloads');
  const prefix = mediaId.slice(0, 8);
  const receiver = globalThis[key];
  const entry = receiver?.entries.get(prefix);
  if (entry && entry.mediaId !== mediaId) {
    throw new Error('Ambiguous Flow download filename');
  }

  if (action === 'finish') {
    if (!entry) return false;
    receiver.entries.delete(prefix);
    if (!receiver.entries.size) {
      if (HTMLAnchorElement.prototype.click === receiver.capture) {
        HTMLAnchorElement.prototype.click = receiver.originalClick;
      }
      delete globalThis[key];
    }
    return true;
  }

  if (action === 'read') {
    if (!entry) throw new Error('The Flow download receiver was lost');
    if (!entry.blob) return entry.error ? {error: entry.error} : null;
    const image = await createImageBitmap(entry.blob);
    const {width, height} = image;
    image.close();
    const data = await new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result.split(',')[1]);
      reader.onerror = () => reject(new Error('Could not read Flow 2K image'));
      reader.readAsDataURL(entry.blob);
    });
    return {data, width, height};
  }

  // A previous invocation may have timed out while Flow was still upscaling.
  if (entry) return 'resumed';
  const owners = [...document.querySelectorAll('flow-grid-tile-container button[aria-expanded="true"]')]
    .filter(button => /^(更多选项|More options)$/i.test(button.getAttribute('aria-label') || ''));
  const owner = owners.length === 1
    ? owners[0].closest('flow-grid-tile-container').querySelector('img[data-media-id]')
    : null;
  if (owner?.getAttribute('data-media-id')?.toLowerCase() !== mediaId) {
    throw new Error('Open the download submenu for the exact Flow image first');
  }
  const choices = [...document.querySelectorAll('button[role="menuitem"]')].filter(button =>
    button.getClientRects().length && !button.disabled && button.getAttribute('aria-disabled') !== 'true'
    && /^2K\s+(已高清重塑|upscaled)$/i.test(button.textContent.trim()));
  if (choices.length !== 1) throw new Error('The Flow 2K download option is unavailable or ambiguous');

  if (!receiver) {
    const entries = new Map();
    const originalClick = HTMLAnchorElement.prototype.click;
    const capture = function (...args) {
      const filenameId = /(?:^|_)([0-9a-f]{8})_2K\.[a-z0-9]+$/i.exec(this.download)?.[1].toLowerCase();
      const pending = entries.get(filenameId);
      if (!pending || !this.href.startsWith('blob:' + location.origin + '/')) {
        return originalClick.apply(this, args);
      }
      // Begin reading synchronously, before Flow revokes its temporary Blob URL.
      if (!pending.reading) {
        pending.reading = true;
        fetch(this.href).then(response => response.blob()).then(blob => {
          if (!blob.type.startsWith('image/') || !blob.size || blob.size > 40000000) {
            throw new Error('Invalid image');
          }
          pending.blob = blob;
        }).catch(() => { pending.error = 'Unable to read the Flow 2K download'; });
      }
    };
    globalThis[key] = {entries, originalClick, capture};
    HTMLAnchorElement.prototype.click = capture;
  }

  globalThis[key].entries.set(prefix, {mediaId});
  choices[0].click();
  return 'started';
}
