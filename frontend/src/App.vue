<script setup>
import { nextTick, onMounted, ref } from 'vue'

const sessionKey = 'sign-in.access-token'
const demoAccount = { username: 'admin', password: '123456' }

const username = ref('')
const password = ref('')
const passwordVisible = ref(false)
const user = ref(null)
const busy = ref(true)
const error = ref('')
const usernameInput = ref(null)
const accountHeading = ref(null)

async function request(path, options, fallback) {
  let response
  try {
    response = await fetch(`/api${path}`, options)
  } catch {
    throw new Error('无法连接登录服务，请稍后重试。')
  }

  const data = await response.json().catch(() => null)
  if (response.ok && data) return data

  const message = typeof data?.detail === 'string' ? data.detail : fallback
  throw new Error(message)
}

function getCurrentUser(token) {
  return request(
    '/users/me',
    { headers: { Authorization: `Bearer ${token}` } },
    '无法读取账户信息，请稍后重试。',
  )
}

onMounted(async () => {
  try {
    const token = sessionStorage.getItem(sessionKey)
    if (token) user.value = await getCurrentUser(token)
  } catch {
    sessionStorage.removeItem(sessionKey)
    error.value = '无法恢复登录，请重新登录。'
  } finally {
    busy.value = false
  }
})

function fillDemoAccount() {
  username.value = demoAccount.username
  password.value = demoAccount.password
  passwordVisible.value = false
  error.value = ''
}

async function signIn() {
  if (busy.value) return

  error.value = ''
  if (!username.value.trim() || !password.value) {
    error.value = '请输入用户名和密码。'
    return
  }

  busy.value = true
  try {
    const form = new URLSearchParams({
      username: username.value.trim(),
      password: password.value,
    })
    const { access_token: token } = await request(
      '/token',
      { method: 'POST', body: form },
      '登录服务暂不可用，请稍后重试。',
    )

    const account = await getCurrentUser(token)
    sessionStorage.setItem(sessionKey, token)
    user.value = account
    password.value = ''
    passwordVisible.value = false
    await nextTick()
    accountHeading.value?.focus()
  } catch (failure) {
    error.value = failure.message
  } finally {
    busy.value = false
  }
}

async function signOut() {
  sessionStorage.removeItem(sessionKey)
  user.value = null
  username.value = ''
  password.value = ''
  error.value = ''
  await nextTick()
  usernameInput.value?.focus()
}
</script>

<template>
  <main class="page">
    <section class="panel" aria-labelledby="page-heading">
      <header class="brand">
        <span class="brand-mark" aria-hidden="true"><span></span></span>
        <span>账户中心</span>
      </header>

      <div v-if="user" class="panel-content">
        <h1 id="page-heading" ref="accountHeading" tabindex="-1">登录成功</h1>
        <p class="intro">你已登录到账户中心。</p>
        <dl class="account-details">
          <div>
            <dt>用户名</dt>
            <dd>{{ user.username }}</dd>
          </div>
          <div>
            <dt>用户 ID</dt>
            <dd>{{ user.id }}</dd>
          </div>
        </dl>
        <button type="button" class="primary-button" @click="signOut">退出登录</button>
      </div>

      <div v-else class="panel-content">
        <h1 id="page-heading">登录账户</h1>
        <p class="intro">请输入用户名和密码继续。</p>
        <form class="login-form" :aria-busy="busy" @submit.prevent="signIn">
          <div class="field">
            <label for="username">用户名</label>
            <input
              id="username"
              ref="usernameInput"
              v-model="username"
              name="username"
              placeholder="输入用户名"
              autocomplete="username"
              autocapitalize="none"
              spellcheck="false"
              required
              :disabled="busy"
              :aria-describedby="error ? 'login-error' : undefined"
              @input="error = ''"
            />
          </div>

          <div class="field">
            <label for="password">密码</label>
            <div class="password-field">
              <input
                id="password"
                v-model="password"
                name="password"
                :type="passwordVisible ? 'text' : 'password'"
                placeholder="输入密码"
                autocomplete="current-password"
                required
                :disabled="busy"
                :aria-describedby="error ? 'login-error' : undefined"
                @input="error = ''"
              />
              <button
                type="button"
                class="visibility-button"
                aria-controls="password"
                :disabled="busy"
                @click="passwordVisible = !passwordVisible"
              >{{ passwordVisible ? '隐藏' : '显示' }}</button>
            </div>
          </div>

          <p v-if="error" id="login-error" class="error" role="alert">{{ error }}</p>

          <button type="submit" class="primary-button" :disabled="busy">
            {{ busy ? '正在验证…' : '登录' }}
            <span v-if="!busy" class="button-arrow" aria-hidden="true">→</span>
          </button>
        </form>

        <div class="demo">
          <p>演示账号 <code>{{ demoAccount.username }}</code> / <code>{{ demoAccount.password }}</code></p>
          <button type="button" :disabled="busy" @click="fillDemoAccount">填入</button>
        </div>
      </div>
    </section>

    <div class="photo" aria-hidden="true"></div>
  </main>
</template>
