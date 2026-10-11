import {defineConfig} from 'vite';
export default defineConfig(({mode})=>({
 publicDir:mode==='aggregate'?'aggregate-public':'public',
 build:{outDir:mode==='aggregate'?'aggregate-dist':'dist'},
}));
