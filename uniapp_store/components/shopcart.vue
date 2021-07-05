<template>
	<view class="shopcart">
		<!-- 购物车 -->
		<view class="cartBottom" @click="toggleList">
			<view class="carIcon">
				<view class="iconBox" :class="getAllCount ? 'active' : '' ">
					<text class="allcount" v-if="getAllCount">{{getAllCount}}</text>
					<image src="../static/cart.png" mode="" class="img"></image>
				</view>
			</view>
			<view class="middle">
				<text class="price" :class="getAllCount ?　'active': ''">￥{{getAllPrice}}</text>

			</view>
			<view class="BtnRight">
				<text @click="onSubmit">提交</text>
			</view>
		</view>
		<!-- 选择的商品 -->
		<view class="cartList" v-show="isShowList && getList.length">
			<scroll-view scroll-y style="max-height: 400px;">
				<view class="title">
					<text>购物车</text>
					<view class="clear" @click="delShopcart">
						清空
					</view>
				</view>
				<view class="list">
					<view class="list-text" v-for="(item,index) in getList" :key="index">
						<text style="flex:1">{{item.name}}</text>
						<text style="flex:1">￥{{item.price}}</text>
						<cartcontrol :food="item" @add="addCart" @dec="decreaseCart"></cartcontrol>
					</view>
				</view>
			</scroll-view>
		</view>
		<view class="listMask" v-show="isShowList && getList.length" @click="toggleList"></view>
		<uni-popup ref="popup" type="center">
			<view class="" style="background-color: #fff;width: 600rpx;height: 300rpx;padding: 20px;">
				<view class="">
					<uni-combox label="店铺名" labelWidth="150px" @inputId="onClickInputId" :itemData="itemData"
						@input="onClickinput" placeholder="请输入店铺名" v-model="city"></uni-combox>
				</view>
				<view class="example-body">
					<combox-search label="送达时间" labelWidth="100px" emptyTips="无匹配选项" :isJSON="true" :keyName="keyName"
						:candidates="candidates" placeholder="请选择送达时间" @getValue="getValue($event,'json')">
					</combox-search>
				</view>
				<view class="btnSubmit" @click.stop="onClickBtn">
					确定
				</view>
			</view>
		</uni-popup>
		<uni-popup ref="popups" type="center">
			<view class="" style="background-color: #fff;width: 600rpx;height: 300rpx;padding: 20px;">

				<view class="example-body">
					<combox-search label="送达时间" labelWidth="100px" emptyTips="无匹配选项" :isJSON="true" :keyName="keyName"
						:candidates="candidates" placeholder="请选择送达时间" @getValue="getValue($event,'json')">
					</combox-search>
				</view>
				<view class="btnSubmit" @click.stop="onClickBtns">
					确定
				</view>
			</view>
		</uni-popup>
	</view>
</template>

<script>
	import cartcontrol from '@/components/cartcontrol.vue'
	import uniPopup from './uni-popup/components/uni-popup/uni-popup.vue'
	import uniCombox from '@/components/uni-combox/uni-combox.vue'
	import comboxSearch from "@/components/cuihai-combox/cuihai-combox.vue"
	import {
		getClientSelectLs,
		AddrationOperate,
		getCommonDataForm
	} from '../api/modules/login.js'

	export default {
		props: {
			goods: {
				type: Array
			},
			type: {
				type: String,
				default: ''
			}
		},
		data() {
			return {
				isShowList: false,
				city: '',
				itemData: [],
				keyName: 'name',
				AreaId: 0,
				candidates: [],
				currentIndex: -1
			};
		},
		components: {
			cartcontrol,
			uniPopup,
			uniCombox,
			comboxSearch
		},
		computed: {

			getList() {
				let result = [];
				this.goods.forEach((good) => {
					good.sku_list.forEach((food) => {
						if (food.count) {
							result.push(food)
						}
					})
				})
				return result
			},
			// 获得购物车所有商品数量
			getAllCount() {
				console.log(this.getList, 'asd')
				let result = 0;
				this.getList.forEach((food) => {
					result += Number(food.count)
				})
				console.log()
				return result
			},
			// 总价
			getAllPrice() {
				let result = 0;
				let result1 = 0;
				this.goods.forEach((good) => {
					good.sku_list.forEach((food) => {
						result1 += this.accMul(food.count, food.real_price)
						result = result1.toFixed(2);
					})
				})
				return result
			}
		},
		created() {
			this.getCommonDataForm()
		},
		methods: {
			getValue(e) {
				this.currentIndex = e
				console.log(e)
			},
			// 获取公共参数
			getCommonDataForm() {
				getCommonDataForm({
					query_type: 'delivery'
				}).then(res => {
					if (res.code == '200') {
						this.candidates = res.data.delivery_ls
					}
				})
			},
			// 点击提交
			onClickBtn() {
				var arr = []
				for (var i = 0; i < this.getList.length; i++) {
					if (this.getList[i].count != 0) {
						let obj = {
							count: this.getList[i].count,
							sku: this.getList[i].id
						}
						arr.push(obj)
					}
				}
				if (this.AreaId != 0 && arr.length != 0 && this.currentIndex >= 0) {
					let params = {
						client_id: this.AreaId,
						delivery_type: this.candidates[this.currentIndex].id,
						goods_data_list: arr
					}

					this.$emit('AddrationOperate', params)

				} else {
					this.$refs.popup.close()
					uni.showToast({
						icon: 'none',
						title: '请选择对应的选项或产品'
					})
				}

				console.log(arr)
			},
			onClickBtns() {
				var arr = []
				for (var i = 0; i < this.getList.length; i++) {
					if (this.getList[i].count != 0) {
						let obj = {
							count: this.getList[i].count,
							sku: this.getList[i].id
						}
						arr.push(obj)
					}
				}
				let params = {
					client_id: this.AreaId,
					goods_data_list: arr,
					delivery_type: this.candidates[this.currentIndex].id

				}
				this.$emit('AddrationOperate', params)
			},
			onClickinput(e) {
				console.log(e)
				getClientSelectLs({
					name: e
				}).then(res => {
					this.itemData = res.data.data
				})
			},
			onClickInputId(e) {
				this.AreaId = e
				console.log(e)
			},
			// 点击提交
			onSubmit() {
				if (this.type == 'edit') {
					this.$refs.popups.open()
					// var arr = []
					// for (var i = 0; i < this.getList.length; i++) {
					// 	if (this.getList[i].count != 0) {
					// 		let obj = {
					// 			count: this.getList[i].count,
					// 			sku: this.getList[i].id
					// 		}
					// 		arr.push(obj)
					// 	}
					// }
					// let params = {
					// 	client_id: this.AreaId,
					// 	goods_data_list: arr
					// }
					// this.$emit('AddrationOperate', params)

				} else {
					this.$refs.popup.open()
				}
			},
			// 解决浮点数 运算出现多位小数
			accMul(arg1, arg2) {
				let m = 0,
					s1 = '',
					s2 = '';
				if (arg1 && arg1 != null)
					s1 = arg1.toString();
				if (arg2 && arg2 != null)
					s2 = arg2.toString();
				// console.log('m1',s2.replace('.',''))
				try {
					m += s1.split('.')[1].length
				} catch (e) {}
				try {
					m += s2.split('.')[1].length
				} catch (e) {}

				return Number(s1.replace('.', '')) * Number(s2.replace('.', '')) / Math.pow(10, m);
			},


			toggleList() {
				console.log('tog')
				if (this.getList.length) {
					// this.isShowList = !this.isShowList;
				}
			},
			delShopcart() {
				this.isShowList = false;
				this.$emit('delAll');
			},
			addCart: function(item) {
				this.$emit('add', item)
			},
			decreaseCart(item) {
				this.$emit('dec', item)
			}

		},
	}
</script>

<style scoped>
	.btnSubmit {
		width: 150rpx;
		height: 60rpx;
		background-color: #007AFF;
		color: #fff;
		margin: 30rpx auto;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.list-text {
		display: flex;
		flex-direction: row;
	}

	.shopcart .cartBottom {
		position: fixed;
		bottom: -1px;
		left: 0;
		right: 0;
		height: 54px;
		z-index: 99;
		display: flex;
		background-color: #141d27;
	}

	.carIcon {
		flex: 1;
	}

	.iconBox {
		position: absolute;
		bottom: 22px;
		left: 18px;
		z-index: 101;
		background-color: rgb(70, 73, 75);
		border-radius: 50%;
		height: 48px;
		width: 48px;
		line-height: 55px;
	}

	.iconBox .allcount {
		position: absolute;
		right: -6px;
		top: 0;
		display: inline-block;
		padding: 0 6px;
		font-size: 9px;
		line-height: 16px;
		font-weight: 400;
		border-radius: 10px;
		background-color: #f01414;
		color: #ffffff;
	}

	.img {
		font-size: 24px;
		line-height: 24px;
		width: 30px;
		height: 30px;
		padding-left: 6px;
		padding-top: 6px;
		color: #cccccc;
		border-radius: 50%;
	}

	.carIcon .active {
		background-color: #00a0dc;
	}

	.middle {
		display: flex;
		flex-direction: column;
		flex: 2;

		align-items: flex-start;
		justify-content: center;
		color: #ffffff;
	}

	.BtnRight {
		flex: 1;
		color: #fff;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.cartList {
		position: fixed;
		bottom: 54px;
		left: 0;
		right: 0;
		z-index: 90;
	}

	.cartList .title,
	.cartList .list-text {
		display: flex;
		flex-direction: row;
	}

	.cartList .title {
		background: #F3F5F7;
		justify-content: space-between;
		padding: 4px 8px;
	}

	.cartList .list-text {
		padding: 10px 6px 10px 8px;
		text-align: center;
	}

	.list {
		background: #F8F8F8;
		padding-bottom: 10px;
	}


	/* 遮布 */
	.listMask {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		z-index: 89;
		opacity: 0.5;
		background: #6a7076;
	}
</style>
