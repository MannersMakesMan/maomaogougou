<template>
	<view class="content">
		<scroll-view class="menu-wrapper" scroll-y :scroll-top="left_scroll" scroll-with-animation="true">
			<view class="left-content">
				<view style="position: relative;" v-for="(item,index) in cartList" :key="index" ref="menuList"
					@click="select(index)" :class="{'current': currentIndex == index}">
					<view class="menu-item">{{item.category}}</view>
					<text class="allcount" v-if="getAllCount>=item.count&&item.count>0">{{item.count}}</text>
				</view>
			</view>
		</scroll-view>
		<!-- 右侧滚动 -->
		<scroll-view class="foods-wrapper" scroll-y :style="'height:'+windows_height+'px'" :scroll-top="foodSTop"
			@scroll="myscroll" scroll-with-animation="true">
			<view ref="foodsWrapper">
				<view ref="foodList" class="foods" v-for="(item, i) in cartList" :key="i">
					<view class="food-title" style="background: #f3f5f7">
						{{item.category}}
					</view>
					<view class="food" v-for="(food, index) in item.sku_list" :key="index">
						<image :src="showImg(food.default_image_url)" mode=""
							style="width: 75px;height: 75px;margin-top: 6px;"></image>
						<view class="food-info">
							<text style="font-size: 15px;margin-top: 2px;">{{food.name}}</text>
							<!-- <text style="font-size: 13px;margin: 2px 0;">{{food.description}}</text> -->
							<text style="font-size: 13px;margin: 2px 0 4px;">库存{{food.stock}}</text>
							<!-- 加减 -->
							<view class="food-btm">
								<text class="food-price">￥{{food.real_price}}</text>
								<cartcontrol :food="food" @add="addCart" @dec="decreaseCart"></cartcontrol>
							</view>
						</view>
					</view>
				</view>
			</view>
		</scroll-view>
		
		<shopcart @AddrationOperate="AddrationOperate" :type="type" :goods="cartList" @add="addCart" @dec="decreaseCart"
			@delAll="delAll"></shopcart>
			<!-- 登录弹框 -->
			<shopro-login-modal></shopro-login-modal>
	</view>
</template>

<script>
	import shopcart from '@/components/shopcart.vue';
	import cartcontrol from '@/components/cartcontrol.vue'
	import Vue from 'vue'
	import {
		GoodsList,
		AddrationOperate
	} from '../../api/modules/login.js'
	import baseUrl from '../../api/config.js'


	export default {
		data() {
			return {
				title: 'Hello',
				windows_height: 0, //屏幕高度
				foodSTop: 0, //右侧的滑动值
				currentIndex: 0,
				last: 0,
				right_height: [], //右侧每个内容的高度集合
				select_index: 0,
				left_height: 0, //左侧总高度
				left_scroll: 0, //左侧滑动值
				catrgoryList: [],
				timeout: null,
				cartList: [],
				params: {},
				type: ''
			}
		},
		components: {
			shopcart,
			cartcontrol
		},
		onLoad(options) {
			if (options.params) {
				this.params = JSON.parse(options.params)
				if (this.params.type == 'edit') {
					this.type = 'edit'
					uni.setNavigationBarTitle({
						title: '修改定量'
					})
				} else {
					this.type = 'add'
					uni.setNavigationBarTitle({
						title: '添加定量'
					})
				}

			} else {

			}
			this.windows_height = Number(uni.getSystemInfoSync().windowHeight) - 55;
			this.getGoodsList()
			setTimeout(() => {
				this.getHeightList();
			}, 1000)
		},

		computed: {

			// 获得购物车所有商品数量
			getAllCount: function(item) {
				let result = [];
				let count = 0;

				for (let i = 0; i < this.cartList.length; i++) {
					count = 0;
					this.cartList[i].sku_list.forEach((food) => {
						if (food.count >= 0) {
							count += food.count
							Vue.set(this.cartList[i], 'count', count)
						}
					})
					result.push(count)
				}

				result.sort(function(a, b) {
					return a - b;
				})
				count = result[result.length - 1]
				return count;
			},

		},
		methods: {
			AddrationOperate(params) {
				params.ration_id = this.type == 'edit' ? this.params.ration_id : ''
				console.log(AddrationOperate, 'aaaaaa')
				AddrationOperate(params).then(res => {
					console.log(res)
					if (res.code == '200') {

						uni.showToast({
							icon: 'none',
							title: '成功'
						})
						setTimeout(() => {
							uni.switchTab({
								url: './index'
							})
						}, 500)
					} else {
						console.log(1)
					}
				})
			},
			// 获取分类列表
			getGoodsList() {
				GoodsList({
					is_ration: this.params.is_ration,
					ration_id: this.params.ration_id
				}).then(res => {
					console.log(res)
					if (res.code == '200') {
						this.cartList = res.data
						console.log(this.cartList)

					} else {
						uni.showToast({
							icon: 'none',
							title: '获取失败'
						})
					}
				})
			},
			showImg(img) {
				return baseUrl + img
			},
			// 点击侧边栏
			select(index) {
				this.currentIndex = index;
				this.setScrollH(index);
			},

			// 设置点击侧边栏右边滚动的高度
			setScrollH: function(index) {
				var that = this;
				let height = 0;
				var query = uni.createSelectorQuery();
				let foods = query.selectAll('.foods');

				this.$nextTick(function() {
					foods.fields({
						size: true
					}, data => {
						if (index == 0) {
							that.foodSTop = 0;
						}
						for (let i = 0; i < index; i++) {

							height += parseInt(data[i].height);
							// console.log('fh', foods);
							that.foodSTop = height;
							// console.log(that.foodSTop)
						}

					}).exec();
				})

			},

			addCart: function(item) {
				if (item.count >= 0) {
					item.count++
					this.cartList.forEach((good) => {
						good.sku_list.forEach((food) => {
							// 根据名字添加购物车,实际环境根据需要更改
							if (item.name == food.name)
								food.count = item.count
						})
					})
				} else {
					console.log('add')
					this.cartList.forEach((good) => {
						good.sku_list.forEach((food) => {
							if (item.name == food.name)
								Vue.set(food, 'count', 1)
						})
					})
				}
			},
			decreaseCart(item) {
				if (item.count) {
					item.count--
					this.cartList.forEach((good) => {
						good.sku_list.forEach((food) => {
							if (item.name == food.name)
								food.count = item.count
						})
					})
				}
			},
			// 清空购物车
			delAll() {
				this.cartList.forEach((good) => {
					good.sku_list.forEach((food) => {
						if (food.count) {
							food.count = 0
						}
					})
				})
			},
			getHeightList() {
				let _this = this;
				let selectorQuery = uni.createSelectorQuery().in(this);
				selectorQuery.select('.left-content').boundingClientRect(function(rects) {
					_this.left_height = rects.height;
				});
				selectorQuery.selectAll('.foods').boundingClientRect(function(rects) {
					_this.right_height = rects.map((item) => item.top);
				}).exec();
			},
			myscroll(e) {
				//引入节流	
				let right_content_height = e.detail.scrollHeight - this.windows_height;
				if (right_content_height == e.detail.scrollTop) {
					return;
				}
				let scroll_top = e.detail.scrollTop + 110; //110是banner图的高度
				//判断当前的scrollTop在哪个区间内;
				let now = +new Date();
				if (now - this.last > 100) {
					this.last = now;
					let active_index = this.right_height.findIndex((value, index, arr) => value <= scroll_top &&
						scroll_top < arr[index + 1]);
					this.currentIndex = active_index;
					if (this.left_height - this.windows_height) {
						//如果有超出部分
						let diff = this.left_height - this.windows_height
						this.left_scroll = Math.round((active_index * diff) / (this.cartList.length - 1))
					}
				}
			}
		}
	}
</script>

<style>
	.content {
		display: flex;
		position: absolute;
		top: 0;
		bottom: 55px;
		width: 100%;
		overflow: hidden;
	}

	.current {
		position: relative;
		z-index: 0;
		background-color: #fff;
		color: #00A0DC;
		border-left: 5px solid #00A0DC;
	}

	.menu-wrapper {
		text-align: center;
		width: 22%;
		display: flex;
		flex-direction: column;
		background: #f3f5f7;

	}

	.menu-item {
		width: 100%;
		display: flex;
		align-items: center;
		justify-content: center;
		height: 50px;
	}

	.allcount {
		position: absolute;
		right: 6px;
		top: 8px;
		display: inline-block;
		padding: 0 4px;
		font-size: 9px;
		line-height: 16px;
		font-weight: 400;
		border-radius: 50%;
		background-color: #f01414;
		color: #ffffff;
	}

	.foods-wrapper {
		margin-left: 4px;
		width: 78%;
	}

	.food,
	.food-btm,
	.content {
		display: flex;
		flex-direction: row;
	}

	.food-title {
		padding: 20rpx;
		font-weight: bold;
	}

	.food-info {
		margin-left: 10px;
		margin-right: 16px;
		display: flex;
		flex-direction: column;
		flex: 2;
	}

	.food-btm {
		justify-content: space-between;
	}

	.food-price {
		color: #f01414;
		font-size: 16px;
	}
</style>
