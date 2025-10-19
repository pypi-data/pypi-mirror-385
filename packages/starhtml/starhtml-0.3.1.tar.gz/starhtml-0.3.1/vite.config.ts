import { defineConfig } from 'vite'

export default defineConfig({
  build: {
    lib: {
      entry: {
        'persist': './typescript/handlers/persist.ts',
        'scroll': './typescript/handlers/scroll.ts', 
        'resize': './typescript/handlers/resize.ts',
        'drag': './typescript/handlers/drag.ts',
        'canvas': './typescript/handlers/canvas.ts',
        'position': './typescript/handlers/position.ts',
        'throttle': './typescript/handlers/throttle.ts',
        'smooth-scroll': './typescript/handlers/smooth-scroll.ts',
        'split': './typescript/handlers/split.ts',
        'index': './typescript/handlers/index.ts'
      },
      formats: ['es'],
      fileName: (format, entryName) => `${entryName}.js`
    },
    outDir: './src/starhtml/static/js/handlers',
    target: 'es2020',
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: false,
        drop_debugger: false,
        pure_funcs: [],
        passes: 2,
        unsafe: true,
        unsafe_comps: true,
        unsafe_math: true,
        unsafe_methods: true,
        reduce_vars: true,
        collapse_vars: true,
        hoist_funs: true,
        hoist_vars: true
      },
      format: {
        comments: false,
        ascii_only: true,
        semicolons: false,
        beautify: false
      },
      mangle: {
        safari10: true,
        toplevel: true,
        eval: true,
        keep_fnames: false,
        reserved: []
      }
    },
    rollupOptions: {
      external: [],
      output: {
        preserveModules: false,
        compact: true,
        generatedCode: {
          constBindings: true,
          arrowFunctions: true
        }
      }
    },
    sourcemap: false,
    emptyOutDir: true,
    reportCompressedSize: true
  },
  esbuild: {
    target: 'es2020',
    format: 'esm',
    legalComments: 'none',
    treeShaking: true
  }
})