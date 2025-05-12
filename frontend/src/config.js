import { dev } from '$app/environment';

export const API_BASE_URL = dev
	? 'http://localhost:5000'
	: 'http://basketlytics.duckdns.org:5000';

