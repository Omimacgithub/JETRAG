/* Sveltekit */
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()]
});

/* Svelte */
//import { svelte } from '@sveltejs/vite-plugin-svelte';

/** @type {import('vite').UserConfig} */
/*
const config = {
	plugins: [svelte()],
	server: {
		port: 3000
	}
};

export default config;
*/
