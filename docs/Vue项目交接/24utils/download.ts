import { ElMessage } from 'element-plus'
import { useI18n } from '@/hooks/web/useI18n'

const { t } = useI18n()

/**
 * Extract filename from Content-Disposition header
 * @param headers - Response headers object
 * @returns Extracted filename or null
 */
const extractFilenameFromHeaders = (headers: any): string | null => {
  if (!headers) return null

  const contentDisposition = headers['content-disposition'] || headers['Content-Disposition']
  if (!contentDisposition) return null

  const match = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
  if (!match) return null

  let filename = match[1]
  // Remove quotes if present
  if (
    (filename.startsWith('"') && filename.endsWith('"')) ||
    (filename.startsWith("'") && filename.endsWith("'"))
  ) {
    filename = filename.substring(1, filename.length - 1)
  }

  // Decode URL-encoded filename
  try {
    return decodeURIComponent(filename)
  } catch {
    return filename
  }
}

/**
 * Parse backend error message from JSON blob response.
 */
const parseBlobErrorMessage = async (blob: Blob): Promise<string | null> => {
  try {
    const text = await blob.text()
    if (!text) return null

    const json = JSON.parse(text)
    return json?.msg || json?.message || null
  } catch {
    return null
  }
}

type SaveWithPickerResult = 'saved' | 'cancelled' | 'unsupported'

/**
 * 优先使用 File System Access API，让用户先选择保存路径。
 */
const saveBlobWithPicker = async (blob: Blob, fileName: string): Promise<SaveWithPickerResult> => {
  const showSaveFilePicker = (window as any).showSaveFilePicker as
    | ((options?: Record<string, unknown>) => Promise<any>)
    | undefined

  if (typeof showSaveFilePicker !== 'function') {
    return 'unsupported'
  }

  try {
    const extension = fileName.includes('.') ? `.${fileName.split('.').pop()}` : ''
    const fileHandle = await showSaveFilePicker({
      suggestedName: fileName,
      types: extension
        ? [
            {
              description: 'File',
              accept: {
                [blob.type || 'application/octet-stream']: [extension]
              }
            }
          ]
        : undefined
    })

    const writable = await fileHandle.createWritable()
    await writable.write(blob)
    await writable.close()

    return 'saved'
  } catch (error: any) {
    // 用户取消保存时不报错、不回退自动下载。
    if (error?.name === 'AbortError') {
      return 'cancelled'
    }
    throw error
  }
}

/**
 * Download file from blob response
 * @param response - Response object or blob
 * @param fileName - Default downloaded file name
 * @param successMessage - Success message
 * @param errorMessage - Error message
 */
export const downloadFile = async (
  response: any,
  fileName: string,
  successMessage: string = t('common.downloadSuccess'),
  errorMessage: string = t('common.downloadFailed')
): Promise<boolean> => {
  try {
    if (!response) {
      ElMessage.error(errorMessage)
      return false
    }

    // Handle different response formats
    const actualBlob =
      response instanceof Blob ? response : response.data instanceof Blob ? response.data : null

    if (!actualBlob) {
      console.error('Invalid blob data:', response)
      ElMessage.error(errorMessage)
      return false
    }

    const headers = response?.headers || {}
    const contentType = (
      headers['content-type'] ||
      headers['Content-Type'] ||
      actualBlob.type ||
      ''
    ).toLowerCase()

    // responseType=blob 时，后端错误常以 JSON blob 返回，需要先识别并阻断成功提示
    if (contentType.includes('application/json') || contentType.includes('text/json')) {
      const serverErrorMessage = await parseBlobErrorMessage(actualBlob)
      ElMessage.error(serverErrorMessage || errorMessage)
      return false
    }

    // Extract filename from headers if available
    let finalFileName = fileName
    const extractedFilename = extractFilenameFromHeaders(headers)
    if (extractedFilename) {
      finalFileName = extractedFilename
    }

    const saveResult = await saveBlobWithPicker(actualBlob, finalFileName)
    if (saveResult === 'saved') {
      if (successMessage) {
        ElMessage.success(successMessage)
      }
      return true
    }

    if (saveResult === 'cancelled') {
      return false
    }

    // 回退到浏览器默认下载行为。
    const url = window.URL.createObjectURL(actualBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = finalFileName
    link.click()
    window.URL.revokeObjectURL(url)

    if (successMessage) {
      ElMessage.success(successMessage)
    }
    return true
  } catch (error) {
    console.error('File download failed:', error)
    ElMessage.error(errorMessage)
    return false
  }
}

/**
 * Handle template download with API call
 * @param apiCall - API function that returns blob
 * @param fileName - Downloaded file name
 * @param successMessage - Success message
 * @param errorMessage - Error message
 */
export const handleTemplateDownload = async (
  apiCall: () => Promise<any>,
  fileName: string,
  successMessage?: string,
  errorMessage?: string
): Promise<boolean> => {
  try {
    const blob = await apiCall()
    return await downloadFile(blob, fileName, successMessage, errorMessage)
  } catch (error) {
    console.error('Template download failed:', error)
    ElMessage.error(errorMessage || t('common.downloadFailed'))
    return false
  }
}
