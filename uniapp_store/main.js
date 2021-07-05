import Vue from 'vue'
import App from './App'
import store from './store/index.js'
import shoproLoginModal from '@/components/gk-login-modal/shopro-login-modal.vue'
Vue.component('shopro-login-modal', shoproLoginModal);

Vue.config.productionTip = false

App.mpType = 'app'
Vue.prototype.$store = store

const app = new Vue({
	...App,
	store
})
app.$mount()
