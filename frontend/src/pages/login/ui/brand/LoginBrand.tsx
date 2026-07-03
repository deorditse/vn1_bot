import {HStack} from '@shared/ui';
import tabletkaLogo from '@shared/assets/tabletka-logo.svg';
import styles from './LoginBrand.module.less';

export function LoginBrand() {
  return (
    <HStack className={styles.brand} gap="12">
      <img alt="Таблетка.ру" src={tabletkaLogo} />
      <div>
        <strong>Bot-api</strong>
      </div>
    </HStack>
  );
}
