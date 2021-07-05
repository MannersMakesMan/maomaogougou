<template>
	<view class="page_box">
		<view class="tool-box x-bc">
			<view class="head_box" v-if="cartList.length" style="width: 100%;">
				<view class="tool-box x-bc">
					<view class="count-box">
						共
						<text class="all-num">{{ cartList.length }}</text>
						件商品
					</view>
					<button class="cu-btn set-btn" @tap="onSet">{{ isTool ? '完成' : '编辑' }}</button>
				</view>
			</view>
		</view>
		<view class="content_box">
			<checkbox-group class="block" v-if="cartList.length != 0">
				<view class="collect-list x-start" v-for="(g, index) in cartList" :key="index">
					<view class="x-c" style="height: 200rpx;" @tap="onSel(index, g.checked)">
						<checkbox :checked="g.checked" :class="{ checked: g.checked }" class="goods-radio round orange">
						</checkbox>
					</view>
					<view class="goods-wrap">
						<view class="goods-box x-start">
							<image class="goods-img" :src="showImg(g.sku.default_image_url)" mode="aspectFill"></image>
							<view class="y-start">
								<view class="goods-title more-t">{{ g.sku.name }}</view>
								<slot name="tipTag"></slot>
								<view class="size-tip">{{ g.sku.goods_sku_text ? g.sku.goods_sku_text : '' }}</view>
								<view class="x-bc price-box">
									<view class="price">￥{{ g.sku.real_price }}</view>
									<view class="num-step">
										<uni-number-box @change="onChangeNum($event, g, index)" :value="g.num" :step="1"
											:min="0"></uni-number-box>
									</view>
								</view>
							</view>
						</view>
					</view>
				</view>
			</checkbox-group>
			<block v-if="cartList.length == 0">
				<view class="empty-box x-c">
					<shopro-empty :emptyData="emptyData"></shopro-empty>
				</view>
			</block>
		</view>
		<view class="foot_box " v-if="cartList.length">
			<view class="tools-box x-bc">
				<label class="check-all x-f" @tap="onAllSel">
					<radio :checked="allSel" :class="{ checked: allSel }" class="check-all-radio orange"></radio>
					<text>全选</text>
					<text>（{{ totalCount.totalNum }}）</text>
				</label>
				<view class="x-f">
					<view class="price" v-if="!isTool">￥{{ totalCount.totalPrice.toFixed(2) }}</view>
					<button class="cu-btn pay-btn" :disabled="!isSel" v-show="!isTool" @tap="onPay">结算</button>
					<button class="cu-btn del-btn" v-show="isTool" @tap="goodsDelete">删除</button>
				</view>
			</view>
		</view>
		<!-- 登录弹框 -->
		<shopro-login-modal></shopro-login-modal>
	</view>
</template>

<script>
	import shoproEmpty from '../../components/shopro-empty/shopro-empty.vue'
	import {
		shopCartList
	} from '../../api/modules/login.js'
	import baseUrl from '../../api/config.js'
	import {
		mapMutations,
		mapActions,
		mapState,
		mapGetters
	} from 'vuex';

	export default {
		components: {
			shoproEmpty
		},
		data() {
			return {
				emptyData: {
					img: `https://shopro.7wpp.com/imgs/empty/emptyCart.png`,
					tip: '购物车空空如也,快去逛逛吧~'
				},
				isTool: false
			};
		},
		onShow() {
			this.getCartList()
			console.log(this.cartList)
		},
		computed: {
			...mapState({
				cartList: state => state.login.cartList,
				allSel: state => state.login.allSelected,
			}),
			...mapGetters(['totalCount', 'isSel'])
		},
		methods: {
			...mapActions(['getCartList', 'changeCartList', 'changeCartListEdit']),
			// 结算
			onPay() {
				if (this.isSel) {
					let confirmcartList = [];
					this.cartList.forEach(item => {
						if (item.checked) {
							confirmcartList.push({
								goods_id: item.id,
								goods_num: item.num,
								goods_name: item.sku.name,
								goods_img: baseUrl + item.sku.default_image_url,
								goods_price: item.real_total_price,
								
							});
						}
					});
					console.log(confirmcartList,'confirmcartList')
					uni.navigateTo({
						url: '../Order/Order?goods_info=' + JSON.stringify(confirmcartList) + '&totle_price=' +
							this.totalCount.totalPrice.toFixed(2) + '&order_type=' + 2
					})
				}
			},
			// 删除
			goodsDelete() {
				let that = this;
				let {
					cartList
				} = this;
				let selectedIdsArray = [];
				cartList.map(item => {
					if (item.checked) {
						selectedIdsArray.push(item.id);
					}
				});
				this.changeCartList({
					ids: selectedIdsArray,
					art: 'delete'
				});
			},
			// 全选
			onAllSel() {
				let that = this;
				that.$store.commit('changeAllSellect'); //按钮切换全选。
				that.$store.commit('getAllSellectCartList', that.allSel); //列表全选
			},
			// 更改商品数
			async onChangeNum(e, g, index) {
				if (g.num !== e) {
					uni.showLoading({
						mask: true
					});
					this.$set(this.cartList[index], 'num', +e);
					await this.changeCartListEdit({
						id: g.id,
						num: e,
						art: 'edit'
					});
					await uni.hideLoading();
				}
			},
			// 功能切换
			onSet() {
				this.isTool = !this.isTool;
			},
			// 单选
			onSel(index, flag) {
				let that = this;
				that.$store.commit('selectItem', {
					index,
					flag
				});
			},
			showImg(img) {
				return baseUrl + img
			},
		}
	}
</script>

<style lang="less">
	.tools-box {
		height: 100rpx;
		width: 750rpx;
		padding: 0 20rpx;
		background: #fff;

		.check-all {
			font-size: 26rpx;

			.check-all-radio {
				transform: scale(0.7);
				color: #e9b564;
			}
		}

		.price {
			color: #e1212b;
			font-size: 500;
			margin-right: 30rpx;
		}

		.pay-btn {
			width: 200rpx;
			height: 70rpx;
			background: linear-gradient(90deg, rgba(233, 180, 97, 1), rgba(238, 204, 137, 1));
			box-shadow: 0px 7rpx 6rpx 0px rgba(229, 138, 0, 0.22);
			border-radius: 35rpx;
			padding: 0;
			color: rgba(#fff, 0.9);
		}

		.del-btn {
			width: 200rpx;
			height: 70rpx;
			background: linear-gradient(90deg, rgba(244, 71, 57, 1) 0%, rgba(255, 102, 0, 1) 100%);
			border-radius: 35rpx;
			padding: 0;
			color: rgba(#fff, 0.9);
		}
	}

	.tool-box {
		height: 90rpx;
		padding: 0 30rpx;
		background: #f7f5f6;

		.count-box {
			font-size: 26rpx;
			color: #999;

			.all-num {
				color: #a8700d;
			}
		}

		.set-btn {
			background: none;
			font-size: 26rpx;
			color: #a8700d;
		}
	}

	.price-box {
		width: 420rpx;

		.price {
			color: #e1212b;
		}
	}

	.goods-box {
		position: relative;

		.goods-img {
			height: 180rpx;
			width: 180rpx;
			background-color: #ccc;
			margin-right: 25rpx;
		}

		.order-goods__tag {
			position: absolute;
			top: 0;
			left: 0;
			z-index: 5;

			.tag-img {
				width: 60rpx;
				height: 30rpx;
			}
		}

		.goods-title {
			font-size: 28rpx;
			font-family: PingFang SC;
			font-weight: 500;
			color: rgba(51, 51, 51, 1);
			width: 450rpx;
			line-height: 40rpx;
			margin-bottom: 10rpx;
		}

		.size-tip {
			line-height: 40rpx;
			// background: #f4f4f4;
			// padding: 0 16rpx;
			font-size: 24rpx;
			color: #666;
		}

		.sub-tip {
			width: 480rpx;
			line-height: 40rpx;
			// background: #F6F2EA;
			font-size: 24rpx;
			color: #a8700d;
			margin: 10rpx 0;
		}

		.price {
			color: #e1212b;
		}
	}

	.content_box {
		flex: 1;
		overflow-y: auto;
	}

	.collect-list {
		padding: 30rpx 20rpx;
		background: #fff;
		margin-bottom: 20rpx;

		/deep/ .goods-title {
			width: 420rpx !important;
		}

		// 商品卡片包裹
		.goods-wrap {
			position: relative;

			.lose-box {
				position: absolute;
				z-index: 10;
				width: 100%;
				height: 100%;
				background-color: rgba(#fff, 0.8);

				.icon-yishixiao {
					position: absolute;
					bottom: 0rpx;
					right: 80rpx;
					font-size: 140rpx;
					line-height: 140rpx;
					color: #dbdbdb;
					transform: rotate(-30deg);
				}

				.invalid-tips {
					position: absolute;
					top: 0;
					right: 0;
					left: 0;
					bottom: 0;
					margin: auto;
					width: 400rpx;
					height: 60rpx;
					border-radius: 30rpx;
					color: #fff;
					background-color: rgba(#000, 0.35);
				}
			}
		}

		.tag-box {
			.tag1 {
				line-height: 36rpx;
				padding: 0 8rpx;
				font-size: 18rpx;
				color: rgba(#fff, 0.9);
				background: #f39800;
				display: inline-block;
				box-sizing: border-box;
			}

			.tag2 {
				line-height: 34rpx;
				padding: 0 8rpx;
				font-size: 18rpx;
				color: rgba(#f39800, 0.9);
				background: #fff;
				border-top: 1rpx solid #f39800;
				border-right: 1rpx solid #f39800;
				border-bottom: 1rpx solid #f39800;
				display: inline-block;
				box-sizing: border-box;
			}
		}

		.goods-radio {
			transform: scale(0.7);
			margin-right: 20rpx;
			// background:  #E9B564;
		}

		.price-box {
			width: 420rpx;

			.price {
				color: #e1212b;
			}
		}
	}

	// 空白页
	.empty-box {
		flex: 1;
		width: 100%;
		height: 100%;
	}
</style>
