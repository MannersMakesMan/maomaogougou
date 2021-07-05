<template>
	<view>
		<view class="goodes_detail_swiper-box">
			<!-- 详情轮播 -->
			<swiper class="carousel" circular @change="swiperChange" :autoplay="true">
				<swiper-item @tap="tools.previewImage(imageList,swiperCurrent)" v-for="(img, index) in imageList"
					:key="index" class="carousel-item">
					<image class="swiper-image shopro-selector-rect" :src="img" mode="aspectFill" lazy-load></image>
				</swiper-item>
			</swiper>
			<view v-if="imageList" class="swiper-dots">{{ swiperCurrent + 1 }} / {{ imageList.length }}</view>
		</view>
		<!-- 正常商品 -->
		<view class="normal-price-box">
			<view class="shopro-selector-rect">
				<text class="unit">￥</text>
				<text class="price">{{ goodsInfo.real_price }}</text>
				<text class="notice">优惠价</text>
			</view>
			<view class="x-bc price-bottom-box">
				<view class="x-f shopro-selector-rect">
					<view class="original-price">原价：￥{{goodsInfo.price}}</view>
					<text class="line"></text>
					<view class="sold">库存：{{goodsInfo.stock}}件</view>
				</view>
				<view class="express"></view>
			</view>
		</view>
		<view class="goods-title more-t">{{ goodsInfo.name }}</view>
		<view class="sub-title more-t">{{ goodsInfo.category }}</view>
		<view class="tab-detail pb20">
			<rich-text :nodes="goodsInfo.content"></rich-text>
		</view>
		<!-- 购物车 -->
		<view class="detail-foot_box x-f">
			<view class="left x-f">
				<view class="tools-item y-f" @tap="goHome">
					<image class="tool-img shopro-selector-circular" src="../../static/tabbar/tab_home_sel.png" mode="">
					</image>
					<text class="tool-title shopro-selector-rect">首页</text>
				</view>
			</view>
			<view class="detail-right">
				<view class="detail-btn-box x-ac">
					<button class="cu-btn tool-btn add-btn" @tap="addCart">加入购物车</button>
					<button class="cu-btn tool-btn pay-btn" @tap="goPay">立即购买</button>
				</view>
			</view>
			<uni-popup ref="popup" type="bottom">
				<view class="" style="background-color: #fff;padding: 20rpx;">
					<view class="top x-f modal-head__box">
						<image class="shop-img" :src="showImg(goodsInfo.default_image_url)" mode="aspectFill"></image>
						<view class="y-bc goods-box">
							<view class="goods-title more-t">{{ goodsInfo.name }}</view>
							<view class="x-bc goods-bottom">
								<view class="price-box x-f">
									<view>{{goodsInfo.real_price }}
									</view>
									<!-- <view v-else-if="grouponBuyType === 'groupon'">
										￥{{ currentSkuPrice.groupon_price || (goodsInfo.activity_type === 'groupon' ? goodsInfo.groupon_price : goodsInfo.price) }}
									</view>
									<view v-else>￥{{ currentSkuPrice.price || goodsInfo.price }}</view> -->
								</view>
								<text class="stock">库存{{ goodsInfo.stock }}件</text>
							</view>
						</view>
					</view>
					<view class="buy-num-box x-bc" v-if="goodsInfo.stock != 0">
						<view class="num-title">购买数量</view>
						<view class="num-step">
							<uni-number-box @change="changeNum" :step="1" :min="0" :disabled="disabled"
								:value="goodsNum">
							</uni-number-box>
						</view>
					</view>
					<view class="btn-box foot_box x-bc">
						<button class="cu-btn  cart-btn" @tap="confirmCart">加入购物车</button>
						<button class="cu-btn  buy-btn" @tap="confirmBuy">立即购买</button>
					</view>
				</view>

			</uni-popup>
		</view>
		<!-- 登录弹框 -->
		<shopro-login-modal></shopro-login-modal>
	</view>
</template>

<script>
	import uniPopup from '../../components/uni-popup/components/uni-popup/uni-popup.vue'
	import baseUrl from '../../api/config.js'
	import {
		shopCartUpdate
	} from '../../api/modules/login.js'
	import {
		mapMutations,
		mapActions,
		mapState,
		mapGetters
	} from 'vuex';

	export default {
		components: {
			uniPopup
		},
		data() {
			return {
				goodsInfo: {},
				imageList: [],
				swiperCurrent: 0,
				goodsNum: 0,
				disabled: false,
				content: '<img style="width: 100%;!important" src="https://api.7wpp.com/uploads/20210315/2b165ace71e8f4d327f3b804406046f2.jpg" alt="" /><img style="width: 100%;!important" src="https://api.7wpp.com/uploads/20210315/4ed81351ae14c986113e694f5910970e.jpg" alt="" /><img style="width: 100%;!important" src="https://api.7wpp.com/uploads/20210315/f076bd37e04c4af8560bd0af8c7a06a3.jpg" alt="" />'
			};
		},
		onLoad(options) {
			this.goodsInfo = JSON.parse(options.goods)
			this.imageList = this.goodsInfo.images.map(item => {
				item = baseUrl + item
				return item
			})
			this.goodsInfo.content = this.goodsInfo.content.replace(/<p([\s\w"=\/\.:;]+)((?:(style="[^"]+")))/ig, '<p')
				.replace(/<p>/ig, '<p style="font-size: 15px; line-height: 25px;">')
				.replace(/<img([\s\w"-=\/\.:;]+)((?:(height="[^"]+")))/ig, '<img$1')
				.replace(/<img([\s\w"-=\/\.:;]+)((?:(width="[^"]+")))/ig, '<img$1')
				.replace(/<img([\s\w"-=\/\.:;]+)((?:(style="[^"]+")))/ig, '<img$1')
				.replace(/<img([\s\w"-=\/\.:;]+)((?:(alt="[^"]+")))/ig, '<img$1')
				.replace(/<img([\s\w"-=\/\.:;]+)/ig, '<img style="width: 100%;" $1');
			console.log(this.imageList)
			console.log(JSON.parse(options.goods))
		},
		computed: {
			...mapGetters(['totalCount'])
		},
		methods: {
			goHome() {
				uni.navigateTo({
					url: '../index/index'
				})
			},
			// 加入购物车
			addCart() {
				this.$refs.popup.open()
			},
			// 立即购买
			goPay() {
				if (Boolean(uni.getStorageSync('token'))) {
					this.$refs.popup.open()
				} else {
					this.$store.commit('LOGIN_TIP', true);
				}
			},
			showImg(img) {
				return baseUrl + img
			},
			swiperChange(e) {
				const index = e.detail.current;
				this.swiperCurrent = index;
			},
			changeNum(e) {
				this.goodsNum = Number(e)
			},
			// 立即购买
			confirmBuy() {
				console.log(this.goodsInfo)
				if (Number(this.goodsInfo.stock) >= this.goodsNum) {
					if (this.goodsNum != 0) {
						let confirmGoodsList = [];
						confirmGoodsList.push({
							goods_id: this.goodsInfo.id,
							goods_num: this.goodsNum,
							goods_name: this.goodsInfo.name,
							goods_img: baseUrl + this.goodsInfo.default_image_url,
							goods_price: this.goodsInfo.real_price,
							order_type: 1
						});
						uni.navigateTo({
							url: '../Order/Order?goods_info=' + JSON.stringify(confirmGoodsList) +
								'&totle_price=' +
								this
								.totalCount.totalPrice.toFixed(2) + '&order_type=' + 1
						})
					} else {
						uni.showToast({
							icon: 'none',
							title: '商品数量不能为0'
						})
					}
				} else {

					uni.showToast({
						icon: 'none',
						title: '库存不足'
					})
				}
			},
			// sku加入购物车
			confirmCart() {
				if (Number(this.goodsInfo.stock) >= this.goodsNum) {

					if (this.goodsNum != 0) {

						let datas = {
							count: Number(this.goodsNum),
							sku: this.goodsInfo.id,
						}
						shopCartUpdate(datas).then(res => {
							if (res.code == '200') {
								uni.showToast({
									icon: 'none',
									title: '加入成功！'
								})
								this.$refs.popup.close()
							} else {
								uni.showToast({
									icon: 'none',
									title: '加入失败！'
								})
							}
						})
					} else {
						uni.showToast({
							icon: 'none',
							title: '商品数量不能为0'
						})
					}
				} else {
					uni.showToast({
						icon: 'none',
						title: '库存不足'
					})
				}

			}
		}
	}
</script>

<style lang="less">
	.btn-box {
		height: 100rpx;

		.cu-btn {
			width: 340rpx;
			height: 70rpx;
			border-radius: 35rpx;
			font-size: 28rpx;
			font-family: PingFang SC;
			font-weight: 500;
			color: rgba(255, 255, 255, 0.9);
			padding: 0;
		}

		.cart-btn {
			background: linear-gradient(90deg, rgba(103, 104, 105, 1), rgba(82, 82, 82, 1));
			box-shadow: 0px 2rpx 5rpx 0px rgba(102, 103, 104, 0.46);
		}

		.buy-btn {
			background: linear-gradient(90deg, rgba(233, 180, 97, 1), rgba(238, 204, 137, 1));
			box-shadow: 0px 7rpx 6rpx 0px rgba(229, 138, 0, 0.22);
		}

		.seckill-btn {
			width: 710rpx;
			height: 70rpx;
			background: linear-gradient(90deg, rgba(233, 180, 97, 1), rgba(238, 204, 137, 1));
			box-shadow: 0px 7rpx 6rpx 0px rgba(229, 138, 0, 0.22);
			font-size: 28rpx;
			font-family: PingFang SC;
			font-weight: 500;
			color: rgba(255, 255, 255, 1);
			border-radius: 35rpx;
			padding: 0;
		}
	}

	.buy-num-box {
		.num-title {
			font-size: 26upx;
			font-family: PingFang SC;
			font-weight: 400;
			margin-bottom: 20upx;
		}
	}

	.top {
		margin-bottom: 50upx;

		.shop-img {
			width: 160upx;
			height: 160upx;
			border-radius: 6upx;
			margin-right: 30upx;
			background: #ccc;
		}

		.goods-box {
			height: 160upx;
			width: 490rpx;
			align-items: flex-start;

			.goods-title {
				font-size: 28rpx;
				font-family: PingFang SC;
				font-weight: 500;
				color: rgba(51, 51, 51, 1);
				line-height: 42rpx;
				text-align: left;
			}

			.goods-bottom {
				width: 100%;
			}

			.price-box {
				font-size: 36upx;
				font-family: PingFang SC;
				font-weight: bold;
				color: #e1212b;

				.unit {
					font-size: 24upx;
					font-family: PingFang SC;
					font-weight: bold;
					color: #e1212b;
				}
			}

			.stock {
				font-size: 26rpx;
				color: #999;
			}
		}
	}

	.x-ac {
		display: flex;
		justify-content: space-around;
		align-items: center;
	}

	// 底部工具栏
	.detail-foot_box {
		height: 100rpx;
		background: rgba(255, 255, 255, 1);
		border-top: 1rpx solid rgba(238, 238, 238, 1);
		width: 100%;
		position: fixed;
		bottom: 0;
		z-index: 999;

		.left,
		.detail-right {
			flex: 1;
		}

		.tools-item {
			flex: 1;
			height: 100%;

			.tool-img {
				width: 46rpx;
				height: 46rpx;
			}

			.tool-title {
				font-size: 22rpx;
				line-height: 22rpx;
				padding-top: 8rpx;
			}
		}

		.detail-btn-box {
			flex: 1;

			.tool-btn {
				font-size: 28rpx;
				font-weight: 500;
				color: rgba(#fff, 0.9);
				width: 210rpx;
				height: 70rpx;
				border-radius: 35rpx;
				padding: 0;
				margin-right: 20rpx;

				.price {
					font-size: 24rpx;
					font-weight: bold;
					color: rgba(#fff, 0.9);
				}

				.price-title {
					font-size: 20rpx;
					font-weight: 500;
					color: rgba(#fff, 0.9);
					padding-top: 8rpx;
				}
			}

			.add-btn {
				box-shadow: 0px 2rpx 5rpx 0px rgba(102, 103, 104, 0.46);
				background: linear-gradient(90deg, rgba(103, 104, 105, 1), rgba(82, 82, 82, 1));
			}

			.pay-btn {
				box-shadow: 0px 7rpx 6rpx 0px rgba(229, 138, 0, 0.22);
				background: linear-gradient(90deg, rgba(233, 180, 97, 1), rgba(238, 204, 137, 1));
			}

			.seckill-btn {
				width: 432rpx;
				height: 70rpx;
				background: linear-gradient(93deg, rgba(208, 19, 37, 1), rgba(237, 60, 48, 1));
				box-shadow: 0px 7rpx 6rpx 0px rgba(#ed3c30, 0.22);
				font-size: 28rpx;
				font-family: PingFang SC;
				font-weight: 500;
				color: rgba(255, 255, 255, 1);
				border-radius: 35rpx;
				padding: 0;
				margin-right: 20rpx;
			}

			.seckilled-btn {
				width: 432rpx;
				height: 70rpx;
				background: rgba(221, 221, 221, 1);
				font-size: 28rpx;
				font-family: PingFang SC;
				font-weight: 500;
				color: #999999;
				border-radius: 35rpx;
				padding: 0;
				margin-right: 20rpx;
			}

			.groupon-btn {
				width: 210rpx;
				height: 70rpx;
				background: linear-gradient(90deg, rgba(254, 131, 42, 1), rgba(255, 102, 0, 1));
				box-shadow: 0px 7rpx 6rpx 0px rgba(255, 104, 4, 0.22);
				border-radius: 35rpx;
			}
		}
	}


	.x-f {
		display: flex;
		align-items: center;
	}

	.tab-detail {
		min-height: 300rpx;
		background: #fff;
		background: #fff;
	}

	.goods-title {
		font-size: 28rpx;
		font-weight: 500;
		line-height: 42rpx;
		background-color: #fff;
		padding-bottom: 10rpx;
		padding: 10rpx 20rpx;
	}

	.sub-title {
		padding: 0 20rpx;
		color: #a8700d;
		font-size: 24rpx;
		font-weight: 500;
		line-height: 42rpx;
		background-color: #fff;
		padding-bottom: 10rpx;
	}

	// 正常商品
	.normal-price-box {
		padding: 20rpx;
		background: url('https://shopro.7wpp.com/imgs/price_normal_bg.png') no-repeat;

		background-size: 100% 100%;

		.unit,
		.notice {
			font-size: 24rpx;
			color: #fff;
		}

		.price {
			font-size: 36rpx;
			color: #fff;
			font-weight: bold;
			margin: 0 10rpx;
		}

		.price-bottom-box {
			font-size: 24rpx;
			color: #fff;
			font-weight: 500;
			padding-top: 10rpx;

			.original-price {
				text-decoration: line-through;
			}

			.line {
				margin: 0 20rpx;
				display: inline-block;
				width: 3rpx;
				height: 24rpx;
				background-color: #fff;
			}
		}
	}

	.goodes_detail_swiper-box {
		width: 750rpx;
		height: 750rpx;
		position: relative;

		.carousel {
			width: 750rpx;
			height: 100%;
		}

		.carousel-item {
			width: 750rpx;
			height: 100%;
		}

		.swiper-image {
			width: 750rpx;
			height: 100%;
			background: #ccc;
		}

		.swiper-dots {
			display: flex;
			position: absolute;
			right: 20rpx;
			bottom: 20rpx;
			line-height: 44rpx;
			border-radius: 22rpx;
			padding: 0 15rpx;
			background: rgba(#333, 0.3);
			font-size: 28rpx;
			color: rgba(#fff, 0.9);
		}
	}
</style>
