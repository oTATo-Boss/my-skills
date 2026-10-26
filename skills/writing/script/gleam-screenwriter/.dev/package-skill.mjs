import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import JSZip from 'jszip';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const output=path.resolve(process.argv[2]||'');
if(!process.argv[2])throw new Error('Usage: node package-skill.mjs OUTPUT.zip');
if(fs.existsSync(output))throw new Error('Output already exists; choose a new version/path');
const zip=new JSZip(),hashes=[];
function add(dir){for(const entry of fs.readdirSync(dir,{withFileTypes:true})){
 if(['.dev','.DS_Store','__pycache__','node_modules'].includes(entry.name))continue;
 const file=path.join(dir,entry.name);
 if(entry.isSymbolicLink())throw new Error('Runtime package must not contain symlinks: '+file);
 if(entry.isDirectory()){add(file);continue;}
 if(/\.(tmp|log|pyc)$/.test(entry.name))continue;
 const relative=path.relative(root,file).split(path.sep).join('/');
 const bytes=fs.readFileSync(file);hashes.push(crypto.createHash('sha256').update(bytes).digest('hex')+'  '+relative);
 zip.file('gleam-screenwriter/'+relative,bytes,{unixPermissions:fs.statSync(file).mode&0o777});
}}
add(root);
zip.file('gleam-screenwriter/MANIFEST.sha256',hashes.sort().join('\n')+'\n');
fs.mkdirSync(path.dirname(output),{recursive:true});
const bytes=await zip.generateAsync({type:'nodebuffer',compression:'DEFLATE',compressionOptions:{level:9},platform:'UNIX'});
fs.writeFileSync(output,bytes,{flag:'wx'});
console.log(JSON.stringify({zip:output,bytes:bytes.length,runtimeFiles:hashes.length,excluded:['.dev','node_modules','tests','private data'],sha256:crypto.createHash('sha256').update(bytes).digest('hex')},null,2));
