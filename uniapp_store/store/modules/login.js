import {
	shopCartList,
	shopCartUpdates,
	shopCartUpdateNum
} from '../../api/modules/login.js'
import store from '@/store/index.js'

let login = {
	state: {
		showLoginTip: true,
		userInfo: uni.getStorageSync('userInfo') ? uni.getStorageSync('userInfo') : {},
		cartList: [],
		allSelected: false,
	},
	mutations: {
		LOGIN_TIP(state, data) {
			state.showLoginTip = data
		},
		USER_INFO(state, data) {
			state.userInfo = data
		},
		// 单选设置
		selectItem(
			state, {
				index,
				flag
			}) {
			state.cartList[index].checked = !flag;
			store.commit('checkCartList')

		},
		// 全选检测
		checkCartList(state) {
			let all = true;
			state.cartList.map(item => {
				if (!item.checked) {
					all = false
				}
			})
			state.allSelected = all;
		},
		// 切换全选。
		changeAllSellect(state) {
			state.allSelected = !state.allSelected;
		},
		// 全选设置
		getAllSellectCartList(state, flag) {
			state.cartList.map(item => {
				item.checked = flag
			})
		},
		// cart数据获取变动。
		CART_LIST(state, data) {
			state.cartList = data
		},
	},
	getters: {
		// 购物车数量和总价
		totalCount: state => {
			let totalNum = 0;
			let totalPrice = 0;
			state.cartList.filter(item => {
				if (item.checked) {
					totalNum += 1;
					totalPrice += item.num * item.sku.real_price;
				}
			})
			return {
				totalNum,
				totalPrice
			}
		},
		// 是否选择了商品
		isSel: state => {
			let isSel = false;
			state.cartList.map(item => {
				if (item.checked) {
					isSel = true
				}
			})
			return isSel
		},
	},
	actions: {
		// 购物车数据（查）
		getCartList({
			commit,
			state
		}) {
			return new Promise((resolve, reject) => {
				shopCartList().then(res => {
					res.data.data.forEach(item => {
						item.checked = false
					})
					commit('CART_LIST', res.data.data);
					commit('checkCartList');

				}).catch(e => {
					reject(e)
				})
			})
		},
		// 修改购物车商品数量（改）|| 删除购物车商品（删）
		changeCartList({
			commit,
			state,
			dispatch
		}, param) {
			return new Promise((resolve, reject) => {
				console.log(param)
				shopCartUpdates({
					ids: param.ids,
					// num: param.num || null
				}).then(res => {
					if (param.art === 'delete' && res.code === '200') {
						store.dispatch('getCartList');
					}
					resolve(res)
					commit('checkCartList');
				}).catch(e => {
					reject(e)
				})
			})
		},
		changeCartListEdit({
			commit,
			state,
			dispatch
		}, param) {
			return new Promise((resolve, reject) => {
				console.log(param)
				shopCartUpdateNum({
					id: param.id,
					num: Number(param.num)
				}).then(res => {
					if (param.art === 'delete' && res.code === '200') {
						store.dispatch('getCartList');
					}
					resolve(res)
					commit('checkCartList');
				}).catch(e => {
					reject(e)
				})
			})
		},
	}
}

export default login
