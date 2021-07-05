<template>
	<view style="width: 100%;height: 100%;">
		<view class="" style="">
			<view class="seh-box seh-box-w">
				<view class="serach aSearch-input-box">
					<view class="content" style="border-radius: 60px;">
						<view class="content-box">
							<input :placeholder="defaultKw" confirm-type="search" class="input" v-model="inputVal" />
						</view>
						<view class="serachBtn" @click="doSearch">
							搜索
						</view>
					</view>
				</view>
			</view>
		</view>
		<!-- 添加客户 -->
		<view class="" style="width: 100%;background-color: #efefef;">
			<view class="addBtn" style="" @click="addBtnItem">
				+ 新增
			</view>
			<view class="" style="padding-top: 20rpx;" v-for="(item,index) in newsList" :key="index">
				<view class="item-box">
					<view class="item-name">
						{{item.client_user || '暂无创建人姓名'}}
					</view>
					<view class="" style="width: 650rpx;border: 1rpx solid #DDDDDD;margin: 0 auto;">

					</view>
					<view class="order_details_2">
						<view class="goods">
							<view v-for="(item, index) in item.goods_data" :key="index" class="row">
								<image :src="showImg(item.sku.default_image_url)" mode="scaleToFill" border="0"
									class="pic">
								</image>
								<view class="order_details_10">
									<text decode="true" class="good">{{item.sku.name}}</text>
									<!-- <text decode="true" class="num">数量：{{item.count}}</text> -->
								</view>
								<text decode="true" class="money">数量：{{item.count}}</text>
							</view>
						</view>
					</view>
					<view class=""
						style="display: flex;align-items: center;justify-content: space-between;padding: 20rpx;font-size: 20rpx;">
						<view class="">
							定量单总金额
						</view>
						<view class="">
							{{item.total_amount}}
						</view>
					</view>

					<view class=""
						style="display: flex;align-items: center;justify-content: space-between;padding: 20rpx;">
						<tui-tag margin="20rpx 20rpx 0 0" size="22rpx" padding="12rpx" type="warning"
							@click="onClickDetail(item)">详情
						</tui-tag>
						<tui-tag margin="20rpx 20rpx 0 0" size="22rpx" padding="12rpx" type="green"
							@click="editGoods(item)">修改
						</tui-tag>
						<tui-tag margin="20rpx 20rpx 0 0" size="22rpx" padding="12rpx" type="danger"
							@click="DeleteGoods(item)">删除
						</tui-tag>
					</view>
				</view>
			</view>
			<tui-loadmore :visible="loadding" :index="3" type="red"></tui-loadmore>
			<tui-nomore :visible="!pullUpOn"></tui-nomore>
		</view>
		<!-- 登录弹框 -->
		<shopro-login-modal></shopro-login-modal>
	</view>
</template>

<script>
	import {
		rationOperate,
		DeleterationOperate
	} from '../../api/modules/login.js'
	import baseUrl from '../../api/config.js'

	export default {
		data() {
			return {
				defaultKw: '请输入查询信息',
				kwList: [],
				inputVal: '',
				loadding: false,
				pullUpOn: true,
				PageIndex: 1,
				PageSize: 10,
				newsList: []
			};
		},
		onShow() {
			this.rationOperate()
		},
		// 上拉加载
		async onReachBottom() {
			if (!this.pullUpOn) return;
			this.PageIndex = this.PageIndex + 1;
			this.loadding = true;

			this.rationOperate()
		},
		methods: {
			//执行搜索
			doSearch() {
				rationOperate({
					name: this.inputVal
				}).then(res => {
					if (res.code == '200') {
						this.newsList = res.data.data
					}
				})
			},
			// 新增
			addBtnItem() {
				let params = {
					is_ration: 1,
					type: 'add'
				}
				uni.navigateTo({
					url: './add?params=' + JSON.stringify(params)
				})
			},
			// 详情
			onClickDetail(item) {
				uni.navigateTo({
					url: './detail?data=' + JSON.stringify(item)
				})
			},
			// 修改
			editGoods(item) {
				console.log(item)
				let params = {
					is_ration: 1,
					ration_id: item.id,
					type: 'edit'
				}
				uni.navigateTo({
					url: './add?params=' + JSON.stringify(params)
				})
			},
			// 删除客户
			DeleteGoods(item) {
				DeleterationOperate({
					ids: [item.id]
				}).then(res => {
					if (res.code == '200') {
						uni.showToast({
							icon: 'none',
							title: '删除成功'
						})
						this.rationOperate()
					} else {
						uni.showToast({
							icon: 'none',
							title: '删除失败'
						})
					}
				})
				console.log(item)
			},
			rationOperate() {
				let params = {
					page: this.PageIndex,
					page_size: this.PageSize
				}
				rationOperate(params).then(res => {
					if (res.code == '200') {
						if (!res.data.data || res.data.data.length < this.PageSize) {
							this.pullUpOn = false;
						}
						this.loadding = false;
						if (this.PageIndex == 1) {
							this.newsList = res.data.data
						} else {
							this.newsList = this.newsList.concat(res.data.data)
						}
					}
					console.log(res.data.data)
				})
			},
			showImg(img) {
				return baseUrl + img
			}
		}
	}
</script>

<style lang="less">
	page {
		background-color: rgb(239, 239, 239);
	}

	.order_details_2 .goods {
		white-space: normal;
		width: 690upx;
		min-height: 121upx;
		padding-left: 0upx;
		padding-right: 0upx;
		padding-top: 0upx;
		padding-bottom: 20upx;
		clear: both;
		margin-top: 0upx;
		margin-left: 0upx;
		float: left;
		text-align: left;
		border-bottom-color: #e1e1e1;
		border-bottom-width: 1upx;
		border-bottom-style: solid;
		border-radius: 0upx;
		font-size: 8upx;
	}

	.order_details_2 .goods .row {
		white-space: normal;
		width: 643upx;
		height: 113upx;
		padding: 0upx;
		margin-top: 18upx;
		margin-left: 24upx;
		float: left;
		text-align: left;
		border-radius: 0upx;
		font-size: 8upx;
	}

	.order_details_2 .goods .row .pic {
		white-space: normal;
		width: 91upx;
		height: 90upx;
		padding: 0upx;
		margin-top: 13upx;
		margin-left: 4upx;
		float: left;
		text-align: left;
		border-radius: 0upx;
		font-size: 8upx;
		line-height: 90upx;
	}

	.order_details_1 .order_details_2 .goods .row .order_details_10 .good {
		white-space: normal;
		width: 366upx;
		height: 43upx;
		padding: 0upx;
		clear: both;
		margin-top: 0upx;
		margin-left: 0upx;
		float: left;
		text-align: left;
		border-radius: 0upx;
		color: #646464;
		font-size: 33upx;
		line-height: 43upx;
	}

	.order_details_2 .goods .row .order_details_10 {
		white-space: normal;
		width: 372upx;
		height: 91upx;
		padding: 0upx;
		margin-top: 13upx;
		margin-left: 15upx;
		float: left;
		text-align: left;
		border-radius: 0upx;
		font-size: 8upx;
	}

	.order_details_1 .order_details_2 .goods .row .order_details_10 .num {
		white-space: normal;
		width: 234upx;
		height: 29upx;
		padding: 0upx;
		clear: both;
		margin-top: 12upx;
		margin-left: 0upx;
		float: left;
		text-align: left;
		border-radius: 0upx;
		color: #646464;
		font-size: 22upx;
		line-height: 29upx;
	}

	.order_details_2 .goods .row .money {
		white-space: normal;
		width: 138upx;
		height: 36upx;
		padding: 0upx;
		margin-top: 13upx;
		margin-left: 19upx;
		float: left;
		text-align: right;
		border-radius: 0upx;
		color: #000000;
		font-size: 24upx;
		line-height: 36upx;
	}

	.addBtn {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 100rpx;
		height: 100rpx;
		border-radius: 50%;
		background-color: rgba(80, 212, 212);
		color: #fff;
		font-size: 22rpx;
		position: fixed;
		right: 5%;
		bottom: 15%;
		z-index: 999;
	}

	.item-box {
		width: 690rpx;
		padding-bottom: 20rpx;
		margin: 0 auto;
		background-color: #fff;
		border: 1px solid #F5F5F5;
		border-radius: 20rpx;

		.item-name {
			font-size: 22rpx;
			color: #333;
			font-weight: bold;
			padding: 20rpx;
			// border-bottom: 1rpx solid #DDDDDD;
		}
	}

	.content {
		display: flex;
		align-items: center;
		width: 100%;
		height: 60upx;
		//border: 1px #ccc solid; // 去掉边框
		background: #fff;
		overflow: hidden;
		transition: all 0.2s linear;
		border-radius: 30px;

	}

	.seh-box {
		// width: 100%;
		background-color: rgb(242, 242, 242);

		display: flex;
		justify-content: space-between;
		position: sticky;
		top: 0;
		border: 1rpx solid #efefef;
	}

	.serachBtn {
		height: 100%;
		flex-shrink: 0;
		padding: 0 30upx;
		//按钮背景色
		//background: linear-gradient(to right, #ff9801, #ff570a);
		//background: $uni-color-success;
		line-height: 60upx;
		color: #fff;
		//border-left: 1px #ccc solid; //去掉边框
		transition: all 0.3s;
		background: linear-gradient(to right, rgb(175, 238, 238), rgb(51, 204, 204));
	}


	.content-box {
		width: 100%;
		display: flex;
		align-items: center;


		.input {
			// padding-left: 20upx;
			width: 100%;
			max-width: 100%;
			line-height: 60upx;
			height: 60upx;
			transition: all 0.2s linear;
			font-size: 20rpx;
			padding: 10px;

			&.center {
				width: 200upx;
			}

			&.sub {
				// position: absolute;
				width: auto;
				color: grey;
			}
		}
	}

	.serach {
		display: flex;
		width: 100%;
		box-sizing: border-box;
		font-size: 15px;
	}

	.seh-box .aSearch-input-box {
		width: 100%;
	}

	.seh-box-w {
		width: 95%;
		margin: 0 auto;
	}
</style>
