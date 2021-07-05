import baseUrl from './config'

const API = {
	urls: {},
	extend(obj) {
		this.urls = Object.assign(this.urls, obj);
	},
	dget(name, data) {
		let url = this.urls[name].replace(/\{(.*?)\}/, (s1, s2) => {
			return data[s2];
		});

		return baseUrl + url;
	}
}

export default API
