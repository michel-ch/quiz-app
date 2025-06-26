<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
const emit = defineEmits(['file-change']);
const props = defineProps(['fileDataUrl']);
const isSaving = ref(false);
const fileReader = new FileReader();
const fileInput = ref(null);
const file = ref(null);
const fileDataUrl = ref('');

watch(
  () => props.fileDataUrl,
  (newValue, oldValue) => {
    // console.log('image data from props', newValue.substr(0, 30));
    if (newValue !== oldValue) {
      fileDataUrl.value = newValue;
    }
  }
);

onMounted(() => {
  fileReader.addEventListener(
    'load',
    () => {
      // fileReader holds a b64 string of the image
      fileDataUrl.value = fileReader.result as string;
      isSaving.value = false;
      emit('file-change', fileDataUrl.value);
    },
    false
  );
});
function fileChange(event: { target: any }) {
  isSaving.value = true;
  const input = event.target;
  // pick the first file uploaded
  file.value = input.files[0];
  // set the file into the file reader
  // (next step is in the load eventListener defined in onMounted)
  fileReader.readAsDataURL(file.value);
}
function clickRemoveImageHandler() {
  file.value = null;
  emit('file-change', '');
  if (fileInput.value) {
    fileInput.value.value = '';
  }
}
</script>

<template>
  <div class="flex flex-col gap-4">
    <label
      class="inline-flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded cursor-pointer hover:bg-blue-700 transition duration-150"
    >
      Upload Image
      <input
        type="file"
        accept="image/jpeg, image/png, image/gif"
        class="hidden"
        :disabled="isSaving"
        @change="fileChange"
        ref="fileInput"
      />
    </label>

    <button
      v-if="fileDataUrl"
      type="button"
      class="text-sm text-red-600 hover:underline self-start pb-2"
      @click="clickRemoveImageHandler"
    >
      Remove Image
    </button>
  </div>
</template>
<style scoped>
.remove-link {
  display: block;
}
</style>
