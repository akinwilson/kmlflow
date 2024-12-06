# Common commands 

Short-hands for all resources:

```
kubectl api-resources
```
outputs

```
➜  k8s git:(main) ✗ k api-resources
NAME                                SHORTNAMES   APIVERSION                          NAMESPACED   KIND
bindings                                         v1                                  true         Binding
componentstatuses                   cs           v1                                  false        ComponentStatus
configmaps                          cm           v1                                  true         ConfigMap
endpoints                           ep           v1                                  true         Endpoints
events                              ev           v1                                  true         Event
limitranges                         limits       v1                                  true         LimitRange
namespaces                          ns           v1                                  false        Namespace
nodes                               no           v1                                  false        Node
persistentvolumeclaims              pvc          v1                                  true         PersistentVolumeClaim
persistentvolumes                   pv           v1                                  false        PersistentVolume
pods                                po           v1                                  true         Pod
podtemplates                                     v1                                  true         PodTemplate
replicationcontrollers              rc           v1                                  true         ReplicationController
resourcequotas                      quota        v1                                  true         ResourceQuota
secrets                                          v1                                  true         Secret
serviceaccounts                     sa           v1                                  true         ServiceAccount
services                            svc          v1                                  true         Service
mutatingwebhookconfigurations                    admissionregistration.k8s.io/v1     false        MutatingWebhookConfiguration
validatingadmissionpolicies                      admissionregistration.k8s.io/v1     false        ValidatingAdmissionPolicy
validatingadmissionpolicybindings                admissionregistration.k8s.io/v1     false        ValidatingAdmissionPolicyBinding
validatingwebhookconfigurations                  admissionregistration.k8s.io/v1     false        ValidatingWebhookConfiguration
customresourcedefinitions           crd,crds     apiextensions.k8s.io/v1             false        CustomResourceDefinition
apiservices                                      apiregistration.k8s.io/v1           false        APIService
controllerrevisions                              apps/v1                             true         ControllerRevision
daemonsets                          ds           apps/v1                             true         DaemonSet
deployments                         deploy       apps/v1                             true         Deployment
replicasets                         rs           apps/v1                             true         ReplicaSet
statefulsets                        sts          apps/v1                             true         StatefulSet
selfsubjectreviews                               authentication.k8s.io/v1            false        SelfSubjectReview
tokenreviews                                     authentication.k8s.io/v1            false        TokenReview
localsubjectaccessreviews                        authorization.k8s.io/v1             true         LocalSubjectAccessReview
selfsubjectaccessreviews                         authorization.k8s.io/v1             false        SelfSubjectAccessReview
selfsubjectrulesreviews                          authorization.k8s.io/v1             false        SelfSubjectRulesReview
subjectaccessreviews                             authorization.k8s.io/v1             false        SubjectAccessReview
horizontalpodautoscalers            hpa          autoscaling/v2                      true         HorizontalPodAutoscaler
cronjobs                            cj           batch/v1                            true         CronJob
jobs                                             batch/v1                            true         Job
certificatesigningrequests          csr          certificates.k8s.io/v1              false        CertificateSigningRequest
ingressclassparameterses                         configuration.konghq.com/v1alpha1   true         IngressClassParameters
kongclusterplugins                  kcp          configuration.konghq.com/v1         false        KongClusterPlugin
kongconsumergroups                  kcg          configuration.konghq.com/v1beta1    true         KongConsumerGroup
kongconsumers                       kc           configuration.konghq.com/v1         true         KongConsumer
kongingresses                       ki           configuration.konghq.com/v1         true         KongIngress
konglicenses                        kl           configuration.konghq.com/v1alpha1   false        KongLicense
kongplugins                         kp           configuration.konghq.com/v1         true         KongPlugin
kongupstreampolicies                kup          configuration.konghq.com/v1beta1    true         KongUpstreamPolicy
kongvaults                          kv           configuration.konghq.com/v1alpha1   false        KongVault
tcpingresses                                     configuration.konghq.com/v1beta1    true         TCPIngress
udpingresses                                     configuration.konghq.com/v1beta1    true         UDPIngress
leases                                           coordination.k8s.io/v1              true         Lease
endpointslices                                   discovery.k8s.io/v1                 true         EndpointSlice
events                              ev           events.k8s.io/v1                    true         Event
flowschemas                                      flowcontrol.apiserver.k8s.io/v1     false        FlowSchema
prioritylevelconfigurations                      flowcontrol.apiserver.k8s.io/v1     false        PriorityLevelConfiguration
ingressclasses                                   networking.k8s.io/v1                false        IngressClass
ingresses                           ing          networking.k8s.io/v1                true         Ingress
networkpolicies                     netpol       networking.k8s.io/v1                true         NetworkPolicy
runtimeclasses                                   node.k8s.io/v1                      false        RuntimeClass
poddisruptionbudgets                pdb          policy/v1                           true         PodDisruptionBudget
clusterrolebindings                              rbac.authorization.k8s.io/v1        false        ClusterRoleBinding
clusterroles                                     rbac.authorization.k8s.io/v1        false        ClusterRole
rolebindings                                     rbac.authorization.k8s.io/v1        true         RoleBinding
roles                                            rbac.authorization.k8s.io/v1        true         Role
priorityclasses                     pc           scheduling.k8s.io/v1                false        PriorityClass
csidrivers                                       storage.k8s.io/v1                   false        CSIDriver
csinodes                                         storage.k8s.io/v1                   false        CSINode
csistoragecapacities                             storage.k8s.io/v1                   true         CSIStorageCapacity
storageclasses                      sc           storage.k8s.io/v1                   false        StorageClass
volumeattachments                                storage.k8s.io/v1                   false        VolumeAttachment
```

to retrieve the logs from a cetrain *pod*, do: 

```
kubectl logs etcd-kind-control-plane -n kube-system
```
which will output something like:
```
...
{"level":"info","ts":"2024-12-06T09:30:14.073055Z","caller":"mvcc/kvstore_compaction.go:69","msg":"finished scheduled compaction","compact-revision":166739,"took":"3.057462ms","hash":1626008656,"current-db-size-bytes":2695168,"current-db-size":"2.7 MB","current-db-size-in-use-bytes":1404928,"current-db-size-in-use":"1.4 MB"}
{"level":"info","ts":"2024-12-06T09:30:14.073086Z","caller":"mvcc/hash.go:137","msg":"storing new hash","hash":1626008656,"revision":166739,"compact-revision":166350}
{"level":"info","ts":"2024-12-06T09:35:14.075764Z","caller":"mvcc/index.go:214","msg":"compact tree index","revision":167127}
{"level":"info","ts":"2024-12-06T09:35:14.079036Z","caller":"mvcc/kvstore_compaction.go:69","msg":"finished scheduled compaction","compact-revision":167127,"took":"3.008151ms","hash":1482030526,"current-db-size-bytes":2695168,"current-db-size":"2.7 MB","current-db-size-in-use-bytes":1396736,"current-db-size-in-use":"1.4 MB"}
{"level":"info","ts":"2024-12-06T09:35:14.079069Z","caller":"mvcc/hash.go:137","msg":"storing new hash","hash":1482030526,"revision":167127,"compact-revision":166739}
```

you can even enter running pods and execute arbitrary commands:

```
kubectl exec -it  etcd-kind-control-plane -n kube-system -- sh
```

which will give you a sh terminal into the pod.


