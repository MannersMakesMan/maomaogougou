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
		<view class="" style="width: 100%;">
			<view class="addBtn" style="z-index: 999;" @click="addBtnItem">
				+ 新增
			</view>
			<view class="" style="padding-top: 20rpx;" v-for="(item,index) in newsList" :key="index">
				<view class="item-box">
					<view class="item-name">
						{{item.shop_name || '暂无店铺名'}}
					</view>
					<view class="" style="width: 500rpx;border: 1rpx solid #DDDDDD;margin: 0 auto;">

					</view>
					<view class=""
						style="display: flex;align-items: center;justify-content: space-between;padding: 20rpx;font-size: 20rpx;">
						<view class="">
							手机号
						</view>
						<view class="">
							{{item.phone}}
						</view>
					</view>
					<!-- <view class="" style="display: flex;align-items: center;justify-content: space-between;padding: 20rpx;font-size: 20rpx;">
						<view class="">
							微信号
						</view>
						<view class="">
							{{item.v_chart_number}}
						</view>
					</view> -->
					<view class=""
						style="display: flex;align-items: center;justify-content: space-between;padding: 20rpx;font-size: 20rpx;">
						<view class="">
							详细地址
						</view>
						<view class="">
							{{item.store_address}}
						</view>
					</view>
					<!-- <view class="" style="display: flex;align-items: center;justify-content: space-between;padding: 20rpx;font-size: 20rpx;">
						<view class="">
							店铺名
						</view>
						<view class="">
							{{item.shop_name}}
						</view>
					</view> -->
					<!-- <view class="" style="display: flex;align-items: center;justify-content: space-between;padding: 20rpx;font-size: 20rpx;">
						<view class="">
							客户类型
						</view>
						<view class="">
							{{item.client_type == 1 ? '潜在客户' : '有效客户'}}
						</view>
					</view> -->
					<view class=""
						style="display: flex;align-items: center;justify-content: space-between;padding: 20rpx;font-size: 20rpx;">
						<view class="">
							地址信息
						</view>
						<view class="">
							{{item.address || '无'}}
						</view>
					</view>
					<!-- <view class="" style="display: flex;align-items: center;justify-content: space-between;padding: 20rpx;font-size: 20rpx;">
						<view class="">
							地区
						</view>
						<view class="">
							{{item.address_districts + item.address_city + item.address_provincial}}
						</view>
					</view> -->
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
		getClientLs,
		clientOperateDelete
	} from '../../api/modules/login.js'

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
			this.getClientLs()
		},
		// 上拉加载
		async onReachBottom() {
			if (!this.pullUpOn) return;
			this.PageIndex = this.PageIndex + 1;
			this.loadding = true;

			this.getClientLs()
		},
		methods: {
			//执行搜索
			doSearch() {
				getClientLs({
					name: this.inputVal
				}).then(res => {
					if (res.code == '200') {
						this.newsList = res.data.data
					}
				})
			},
			// 新增
			addBtnItem() {
				uni.navigateTo({
					url: './add'
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
				let params = {
					item: item,
					type: 'edit'
				}
				uni.navigateTo({
					url: './add?params=' + JSON.stringify(params)
				})
			},
			// 删除客户
			DeleteGoods(item) {
				clientOperateDelete({
					ids: [item.id]
				}).then(res => {
					if (res.code == '200') {
						uni.showToast({
							icon: 'none',
							title: '删除成功'
						})
						this.getClientLs()
					} else {
						uni.showToast({
							icon: 'none',
							title: '删除失败'
						})
					}
				})
				console.log(item)
			},
			getClientLs() {
				let params = {
					page: this.PageIndex,
					page_size: this.PageSize
				}
				getClientLs(params).then(res => {
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
			}
		}
	}
</script>

<style lang="less">
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
		bottom: 5%;
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
