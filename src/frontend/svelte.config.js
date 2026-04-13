import adapter from '@sveltejs/adapter-auto';
//import preprocess from 'svelte-preprocess';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';


/** @type {import('@sveltejs/kit').Config} */
/*
const config = {
	// Consult https://github.com/sveltejs/svelte-preprocess
	// for more information about preprocessors
	preprocess: preprocess(),

	kit: {
		adapter: adapter(),
		// vite config is handled separately in vite.config.js
	}
};
*/

const config = {
	// Note the additional `{ script: true }`
	preprocess: vitePreprocess({ script: true })
};


export default config;

