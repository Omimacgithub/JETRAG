import { svelte } from '@sveltejs/vite-plugin-svelte';

/** @type {import('vite').UserConfig} */
const config = {
	plugins: [svelte()],
	server: {
		port: 3000
	}
};

export default config;