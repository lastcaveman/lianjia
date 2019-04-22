import Vue from 'vue'
import VueRouter from 'vue-router'
import HelloWorld from '../components/HelloWorld.vue'
import chart from '../components/chart.vue'

Vue.use(VueRouter)
export default new VueRouter({
  routes: [
    {
      path: '*',
      redirect: '/hotindex'
    },
    {
      path: '/',
      redirect: '/hotindex'
    },
    {
      path: '/hotindex',
      name: 'hotindex',
      component: HelloWorld,
    },
    {
      path: '/chart',
      name: 'chart',
      component: chart,
    }
  ]
});
