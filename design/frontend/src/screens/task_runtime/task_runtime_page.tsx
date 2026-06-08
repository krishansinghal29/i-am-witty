import { IonPage, IonContent } from '@ionic/react';
import { TaskRuntimeHost } from '@/components/task_runtime/host';

/** Full-screen task runtime. Thin wrapper: the host owns all runtime logic. */
export function TaskRuntimePage() {
  return (
    <IonPage>
      <IonContent scrollY={false}>
        <TaskRuntimeHost />
      </IonContent>
    </IonPage>
  );
}
