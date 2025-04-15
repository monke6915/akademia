<template>
<div class="flex justify-center items-center">
    <div class="w-[500px] h-[650px] bg-yellow-500 p-4 rounded-3xl mt-12 mb-4">
    <div class="flex gap-4 justify-center items-center mx-auto">
        <button class="bg-blue-500 text-white p-2 rounded-lg cursor-pointer" @click="addTask()">Add Task</button>
        <input type="text" ref="inputRef" class="w-[300px] p-2 rounded-lg border border-gray-300 bg-gray-300" @keyup.enter="addTask()" placeholder="Add a new task" />
    </div>

    <h1 class="text-2xl font-bold text-center mb-4">TO-DO LIST</h1>

    <div class="flex flex-col gap-4">
        <template v-for="(task, index) in tasks" :key="index">
        <div v-if="!task.deleted" class="flex gap-2 justify-between items-center bg-white p-2 rounded-lg">
            <p>{{ task.name }}</p>
            <input type="checkbox" class="m-2" v-model="task.completed" @change="logTaskStatus(task)" />
            <button class="bg-red-500 text-white p-2 rounded-lg cursor-pointer" @click="task.deleted = true">Delete</button>
        </div>
        </template>
    </div>
	</div>
</div>
</template>


<script setup>
import { ref, watch } from 'vue'


	const tasks = ref(JSON.parse(localStorage.getItem('tasks')) || '[]')

const inputRef = ref(null)

function addTask() {
	const name = inputRef.value.value.trim()
	if (!name.length) return
	const task = {
		name: name,
		completed: false,
		deleted: false

	}
	tasks.value.push(task)
	console.log(tasks.value)
	inputRef.value.value = ''
	
	
	}

	function logTaskStatus(task) {
if (task.completed) {
	console.log(`"${task.name}" is completed `)
} else {
	console.log(`"${task.name}" is not completed`)
}
}







watch(tasks, () => {
    localStorage.setItem('tasks', JSON.stringify(tasks.value))
}, { deep: true })

</script>
