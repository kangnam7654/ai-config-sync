# Java/Kotlin Build Error Resolution

## Diagnostic Commands

```bash
# Step 1: Detect build tool
if [ -f build.gradle ] || [ -f build.gradle.kts ]; then
  ./gradlew build 2>&1
elif [ -f pom.xml ]; then
  mvn compile 2>&1
fi
```

## Common Error Patterns

| Error Pattern | Exact Fix |
|---------------|-----------|
| `cannot find symbol` | Add missing import statement or fix the class/method name |
| `incompatible types` | Add explicit cast or fix the source type |
| `method X in class Y cannot be applied to given types` | Fix the argument types or number of arguments |
| `package X does not exist` | Add missing dependency in `build.gradle` / `pom.xml` |

## Framework-Specific Issues

### Gradle Build Failures

- Run `./gradlew dependencies` to inspect dependency tree for conflicts
- For version conflicts: add explicit `resolutionStrategy.force` in `build.gradle`
- For missing wrapper: run `gradle wrapper` to generate `gradlew`

### Maven Build Failures

- Run `mvn dependency:tree` to inspect dependency tree
- For version conflicts: use `<dependencyManagement>` section in `pom.xml` to pin versions
- For missing artifacts: check that repository is configured in `pom.xml` repositories section

### Kotlin-Specific Errors

- `None of the following candidates is applicable`: check function overloads and named parameter usage
- `Unresolved reference`: add missing import or check Kotlin stdlib version compatibility
