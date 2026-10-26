import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { build } from 'esbuild';
const dev=path.dirname(fileURLToPath(import.meta.url));
const root=path.dirname(dev);
const result=await build({entryPoints:[path.join(dev,'cli.ts')],outfile:path.join(root,'scripts/script-project.cjs'),bundle:true,platform:'node',format:'cjs',target:'node18',tsconfigRaw:{compilerOptions:{baseUrl:path.join(dev,'source'),paths:{'@/*':['./*']}}},nodePaths:[path.join(dev,'node_modules')],legalComments:'inline',metafile:true,treeShaking:true});
fs.writeFileSync(path.join(dev,'build-meta.json'),JSON.stringify(result.metafile,null,2));
fs.chmodSync(path.join(root,'scripts/script-project.cjs'),0o755);
// Preserve published dependency license texts for code bundled into the executable.
const licenses=path.join(root,'references/licenses');fs.mkdirSync(licenses,{recursive:true});
for(const input of Object.keys(result.metafile.inputs)){
 let cursor=path.resolve(input);if(!cursor.includes('node_modules'))continue;
 while(cursor!==path.dirname(cursor)){
  const packageFile=path.join(cursor,'package.json');
  if(fs.existsSync(packageFile)){
   try{const pkg=JSON.parse(fs.readFileSync(packageFile,'utf8'));if(pkg.name){const license=fs.readdirSync(cursor).find(x=>/^licen[cs]e(?:\.|$)/i.test(x));if(license)fs.copyFileSync(path.join(cursor,license),path.join(licenses,pkg.name.replaceAll('/','_')+'.txt'));} }catch{}
   break;
  }
  cursor=path.dirname(cursor);
 }
}
console.log('Built standalone CLI; no npm install required by consumers');
