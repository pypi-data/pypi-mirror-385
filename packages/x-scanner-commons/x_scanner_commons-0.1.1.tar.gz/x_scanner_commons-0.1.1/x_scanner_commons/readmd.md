评估一下 /Users/user/Code/git.evil.pe/x-scanner/x-scanner-commons/x_scanner_commons/infrastructure/vault 这个分层包 /Users/user/Code/git.evil.pe/x-scanner/istio/domain-service/server  能否直接使用？仅评估，不实施。

在创建和修改代码时，应遵循以下原则，并以 **TODO** 形式逐项思考与落实：

1. **充分理解现有代码**
   修改之前必须完整阅读并理解相关模块，确保不重复造轮子，避免因考虑不周带来不合理实现。

**遵循 YAGNI （You Aren’t Gonna Need It）原则** 只有当功能被证明“现在就需要”时才去实现，践行“最好的代码是不存在的代码”。
**保持代码结构合理、优雅、规范** 从整体架构到模块划分、命名、依赖方向等，确保设计清晰且符合团队规范。

4. **提高鲁棒性与可读性**
   关注异常处理、边界条件、测试覆盖率及一致的编码风格，使代码易于维护和扩展。

5. **一次性完整落地实现，避免碎片化版本**
   完成方案后再动手编码，不刻意追求最小改动，也不过度执着向下兼容；直接在原文件、原功能上修改，避免出现 *v2*、*optimize*、*\_advanced* 等多余分支或命名。


请参考 /Users/user/Code/git.evil.pe/x-scanner/x-scanner-commons/x_scanner_commons/infrastructure/vault/docs/BEST_PRACTICES.md 把 shodan 的ak 托管至 vault。ak存放路径为 shodan-service/shodan-api-key。


export VAULT_ADDR='http://172.16.95.75:8200' # x_scanner_commons 会根据环境变量处理，不用再次设置。
export VAULT_NAMESPACE='x-scanner/prod' # x_scanner_commons 会根据环境变量处理，不用再次设置。
vault kv get -mount=secret shodan-service/shodan-api-key # mount 也已经设置好，不用再次设置。

原始的凭据你可以从 /Users/user/Code/git.evil.pe/x-scanner/server-side-main/deploy/overlays/prod/api_keys.toml 获取，然后配置到线上。

去掉原有的环境变量和读配置文件的方式，不要考虑向下兼容，应该彻底的完成迁移。

开发时严格遵循下2条规则。

**遵循 YAGNI （You Aren’t Gonna Need It）原则** 只有当功能被证明“现在就需要”时才去实现，践行“最好的代码是不存在的代码”。
**保持代码结构合理、优雅、规范** 从整体架构到模块划分、命名、依赖方向等，确保设计清晰且符合团队规范。
 