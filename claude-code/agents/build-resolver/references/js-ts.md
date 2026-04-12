# JS/TS Build Error Resolution

## Diagnostic Commands

```bash
# Step 1: Detect package manager
if [ -f pnpm-lock.yaml ]; then PM="pnpm"
elif [ -f yarn.lock ]; then PM="yarn"
elif [ -f package-lock.json ]; then PM="npm"
else PM="npm"; fi

# Step 2: TypeScript type-check (if tsconfig.json exists)
npx tsc --noEmit --pretty --incremental false 2>&1

# Step 3: Project build
$PM run build 2>&1

# Step 4: Lint (non-blocking — run only after build passes)
npx eslint . --ext .ts,.tsx,.js,.jsx 2>&1 || true
```

## Common Error Patterns

| Error Pattern | Exact Fix |
|---------------|-----------|
| `implicitly has 'any' type` | Add explicit type annotation at the declaration |
| `Object is possibly 'undefined'` | Add optional chaining `?.` or nullish coalescing `??` or a null guard |
| `Object is possibly 'null'` | Add null check `if (x !== null)` or non-null assertion `x!` (prefer null check) |
| `Property 'X' does not exist on type 'Y'` | Add property to the interface/type definition, or use type assertion `as` |
| `Cannot find module 'X'` | Check tsconfig `paths`, install missing `@types/X`, or fix the import path |
| `Type 'X' is not assignable to type 'Y'` | Add explicit type cast, fix the source type, or widen the target type |
| `Argument of type 'X' is not assignable to parameter of type 'Y'` | Cast the argument or fix the type at the source |
| `Generic type 'X' requires N type argument(s)` | Add the missing generic parameter(s) |
| `Cannot use JSX unless '--jsx' flag is provided` | Set `"jsx": "react-jsx"` in `tsconfig.json` compilerOptions |
| `Module has no exported member 'X'` | Fix the import name to match the actual export, or add the export |
| `Cannot find name 'X'` | Add import statement or declare the variable/type |
| `'await' expressions are only allowed within async functions` | Add `async` keyword to the containing function |
| `React Hook "useX" is called conditionally` | Move the hook call above all conditional returns |
| `ESM/CJS interop: require() of ES Module` | Change `require()` to dynamic `import()` or set `"type": "module"` |

## Framework-Specific Issues

### Bundler Errors

- **webpack**: Check `webpack.config.*` for loader misconfigurations. Missing loaders for file types produce `Module parse failed` errors.
- **vite**: Check `vite.config.*`. ESM/CJS interop issues often need `ssr.noExternal` or `optimizeDeps.include` adjustments.
- **next.js**: Check `next.config.*`. Server/client boundary errors require `"use client"` or `"use server"` directives.
- **esbuild**: Check `esbuild.*` config. Missing `external` declarations produce bundling failures for Node built-ins.

### `@types/` Mismatch

If the error references `@types/X` version incompatibility:
1. Check the current `@types/X` version in `package.json`
2. Suggest pinning to a compatible version: `{PM} add -D @types/X@{compatible_version}`
3. Do NOT upgrade major versions without user approval
