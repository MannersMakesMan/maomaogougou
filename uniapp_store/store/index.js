import Vue from 'vue';
import Vuex from 'vuex';
import login from './modules/login.js';
import createPersistedState from "vuex-persistedstate";
Vue.use(Vuex);

const store = new Vuex.Store({
	plugins: [
		createPersistedState({
			storage: {
				getItem: key => uni.getStorageSync(key),
				setItem: (key, value) => uni.setStorageSync(key, value),
				removeItem: key => () => {}
			}
		})
	],
	modules: {
		login
	}

});

export default store;
